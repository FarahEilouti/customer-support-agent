
import logging
import os
import time

from google import genai
from google.genai import types
from google.genai.errors import APIError

from support.models import Conversation, Message, AgentAction
from support.services.support_tools import (
    lookup_order,
    search_faq,
    create_support_ticket,
)


logger = logging.getLogger(__name__)


SYSTEM_INSTRUCTION = """
You are a helpful customer support AI agent.

Your responsibilities:
- Answer customer questions using available tools.
- Search the FAQ before answering questions about company policies.
- Check order status using the order lookup tool.
- Create support tickets when the customer explicitly requests
  human assistance or asks to open a ticket.
- Never invent order details or company policies.
- Never claim a ticket was created unless the tool confirms success.
- If information is missing, ask for clarification.
- Keep responses clear, concise, and professional.
"""


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
    if conversation_id:
        conversation = Conversation.objects.get(
            id=conversation_id,
            customer_email__iexact=customer_email,
        )
    else:
        conversation = Conversation.objects.create(
            customer_email=customer_email,
        )

    # 3. Save the customer's message
    Message.objects.create(
        conversation=conversation,
        role=Message.Role.USER,
        content=user_message,
    )

    # Track tools for THIS request only.
    current_tools_used = []

    # Keep a successful ticket result in case Gemini fails later.
    successful_ticket = None

    # 4. Define the tools available to Gemini

    def order_tool(order_number: str) -> dict:
        """Look up the current customer's order by order number."""

        result = lookup_order(
            order_number=order_number,
            customer_email=customer_email,
        )

        current_tools_used.append("lookup_order")

        AgentAction.objects.create(
            conversation=conversation,
            tool_name="lookup_order",
            arguments={"order_number": order_number},
            result=result,
            success=result.get("success", False),
        )

        return result

    def faq_tool(query: str) -> dict:
        """Search the company FAQ knowledge base."""

        result = search_faq(query)

        current_tools_used.append("search_faq")

        AgentAction.objects.create(
            conversation=conversation,
            tool_name="search_faq",
            arguments={"query": query},
            result=result,
            success=result.get("success", False),
        )

        return result

    def ticket_tool(
        title: str,
        description: str,
        priority: str = "medium",
    ) -> dict:
        """Create a human support ticket for the current conversation."""

        nonlocal successful_ticket

        result = create_support_ticket(
            conversation_id=str(conversation.id),
            title=title,
            description=description,
            priority=priority,
        )

        current_tools_used.append("create_support_ticket")

        AgentAction.objects.create(
            conversation=conversation,
            tool_name="create_support_ticket",
            arguments={
                "title": title,
                "description": description,
                "priority": priority,
            },
            result=result,
            success=result.get("success", False),
        )

        if result.get("success"):
            successful_ticket = result

        return result

    # 5. Initialize Gemini
    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

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
        model=os.getenv(
            "GEMINI_MODEL",
            "gemini-3.5-flash-lite",
        ),
        history=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[
                order_tool,
                faq_tool,
                ticket_tool,
            ],
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
        if successful_ticket is not None:
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
    Message.objects.create(
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
