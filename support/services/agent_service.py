
import logging
import time

from django.conf import settings
from google.genai import types
from google.genai.errors import APIError

from support.ai.gemini_client import get_client
from support.ai.prompts import load_system_instruction
from support.models import Message
from support.services.agent_tools import build_tools
from support.services.conversation_service import (
    get_or_create_conversation,
    save_message,
)


logger = logging.getLogger(__name__)


SYSTEM_INSTRUCTION = load_system_instruction()

def run_agent(
    customer_email: str,
    user_message: str,
    conversation_id: str = None,
) -> dict:
    """
    Process a customer message using Gemini and Django tools.
    """

    # 1. Validate inputs
    customer_email = customer_email.strip().lower()
    user_message = user_message.strip()

    if not customer_email or not user_message:
        raise ValueError("Customer email and message are required.")

    # 2. Get or create the conversation
    conversation = get_or_create_conversation(
        customer_email=customer_email,
        conversation_id=conversation_id,
    )

    # 3. Save the customer's message
    save_message(
        conversation=conversation,
        role=Message.Role.USER,
        content=user_message,
    )

    # Track tools for this request only.
    current_tools_used = []

    # Preserve successful ticket information if Gemini fails.
    ticket_state = {"successful_ticket": None}

    # Build tools bound to this conversation and customer.
    tools = build_tools(
        conversation=conversation,
        customer_email=customer_email,
        current_tools_used=current_tools_used,
        ticket_state=ticket_state,
    )

    # 5. Initialize Gemini
    client = get_client()

    # 6. Load previous conversation messages
    history = list(
        conversation.messages.order_by("created_at", "id")
    )

    # The latest user message is sent separately.
    previous_messages = history[:-1]

    contents = [
        types.Content(
            role=(
                "user"
                if message.role == Message.Role.USER
                else "model"
            ),
            parts=[
                types.Part.from_text(text=message.content)
            ],
        )
        for message in previous_messages
    ]

    # 7. Configure Gemini with the three tools
    chat = client.chats.create(
        model=settings.GEMINI_MODEL,
        history=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=tools,
            automatic_function_calling=(
                types.AutomaticFunctionCallingConfig(
                    disable=False,
                    maximum_remote_calls=5,
                )
            ),
        ),
    )

    # 8. Run the agent and measure latency
    start_time = time.perf_counter()

    try:
        response = chat.send_message(user_message)

        answer = (
            response.text
            or "I could not generate a response."
        )

    except APIError:
        logger.exception("Gemini API request failed")

        # The ticket was created successfully in PostgreSQL,
        # but Gemini failed before sending the final response.
        if ticket_state["successful_ticket"] is not None:
            successful_ticket = ticket_state["successful_ticket"]
            answer = (
                "Your support ticket was created successfully. "
                "However, the AI service could not complete "
                "its response. "
                f"Ticket ID: {successful_ticket['ticket_id']}. "
                f"Priority: {successful_ticket['priority']}. "
                f"Status: {successful_ticket['status']}."
            )
        else:
            # No confirmed ticket creation: report the API error.
            raise

    latency_seconds = round(
        time.perf_counter() - start_time,
        3,
    )

    # 9. Save the assistant's final response
    save_message(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        content=answer,
    )

    # 10. Return the result to the Django REST API
    return {
        "conversation_id": str(conversation.id),
        "response": answer,
        "latency_seconds": latency_seconds,
        "tools_used": current_tools_used,
    }