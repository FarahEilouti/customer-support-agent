
from support.models import AgentAction
from support.services.support_tools import (
    lookup_order,
    search_faq,
    create_support_ticket,
)


def build_tools(
    conversation,
    customer_email,
    current_tools_used,
    ticket_state,
):
    """Build tools bound to the current customer and conversation."""

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
            ticket_state["successful_ticket"] = result

        return result

    return [order_tool, faq_tool, ticket_tool]
