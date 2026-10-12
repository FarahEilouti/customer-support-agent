import logging
import os
import time

# orchestartor of he project 

from django.db import transaction
from google import genai
from google.genai import types

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
- Create support tickets when the customer needs human assistance.
- Never invent order details or company policies.
- Never claim that a ticket was created unless the tool confirms success.
- If information is missing, ask the customer for clarification.
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

    customer_email = customer_email.strip().lower()
    user_message = user_message.strip()

    if not customer_email or not user_message:
        raise ValueError("Customer email and message are required.")

    if conversation_id:
        conversation = Conversation.objects.get(
            id=conversation_id,
            customer_email__iexact=customer_email,
        )
    else:
        conversation = Conversation.objects.create(
            customer_email=customer_email,
        )

    Message.objects.create(
        conversation=conversation,
        role=Message.Role.USER,
        content=user_message,
    )

    def order_tool(order_number: str) -> dict:
        """Look up the current customer's order by order number."""

        result = lookup_order(
            order_number=order_number,
            customer_email=customer_email,
        )

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

        result = create_support_ticket(
            conversation_id=str(conversation.id),
            title=title,
            description=description,
            priority=priority,
        )

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

        return result

    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    history = list(
        conversation.messages.order_by("created_at", "id")
    )

    # The latest user message is sent separately below.
    previous_messages = history[:-1]

    contents = [
        types.Content(
            role="user" if message.role == Message.Role.USER else "model",
            parts=[types.Part.from_text(text=message.content)],
        )
        for message in previous_messages
    ]

    chat = client.chats.create(
        model=os.getenv("GEMINI_MODEL", "gemini-3.5-flash"),
        history=contents,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_INSTRUCTION,
            tools=[order_tool, faq_tool, ticket_tool],
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=False,
                maximum_remote_calls=5,
            ),
        ),
    )

    start_time = time.perf_counter()

    try:
        response = chat.send_message(user_message)
        answer = response.text or "I could not generate a response."
    except Exception:
        logger.exception("Gemini agent request failed")
        raise

    latency_seconds = round(time.perf_counter() - start_time, 3)

    Message.objects.create(
        conversation=conversation,
        role=Message.Role.ASSISTANT,
        content=answer,
    )

    return {
        "conversation_id": str(conversation.id),
        "response": answer,
        "latency_seconds": latency_seconds,
        "tools_used": list(
            conversation.agent_actions.order_by("created_at", "id")
            .values_list("tool_name", flat=True)
        ),
    }