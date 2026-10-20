from django.db import DatabaseError, transaction
from support.models import Conversation, SupportTicket


def create_support_ticket(
    conversation_id: str,
    title: str,
    description: str,
    priority: str = "medium",
) -> dict:
    """
    Create a support ticket linked to an existing conversation.
    """
    title = title.strip()
    description = description.strip()
    priority = priority.strip().lower()

    if not title or not description:
        return {
            "success": False,
            "error": "Ticket title and description are required.",
        }

    valid_priorities = {
        choice.value for choice in SupportTicket.Priority
    }

    if priority not in valid_priorities:
        return {
            "success": False,
            "error": "Priority must be low, medium, or high.",
        }

    try:
        with transaction.atomic():
            conversation = Conversation.objects.get(
                id=conversation_id
            )

            ticket = SupportTicket.objects.create(
                conversation=conversation,
                customer_email=conversation.customer_email,
                title=title,
                description=description,
                priority=priority,
            )

    except (Conversation.DoesNotExist, ValueError, TypeError):
        return {
            "success": False,
            "error": "Conversation not found.",
        }
    except DatabaseError:
        return {
            "success": False,
            "error": "Ticket creation is temporarily unavailable.",
        }

    return {
        "success": True,
        "ticket_id": ticket.id,
        "status": str(ticket.status),
        "priority": str(ticket.priority),
    }
