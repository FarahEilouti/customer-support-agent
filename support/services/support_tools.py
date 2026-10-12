from django.db import DatabaseError, transaction

from support.models import (
    Order,
    FAQEntry,
    Conversation,
    SupportTicket,
)


def lookup_order(order_number: str, customer_email: str) -> dict:
    """
    Retrieve an order only when its number and customer email match.
    """
    order_number = order_number.strip().upper()
    customer_email = customer_email.strip()

    if not order_number or not customer_email:
        return {
            "success": False,
            "error": "Order number and customer email are required.",
        }

    try:
        order = Order.objects.filter(
            order_number__iexact=order_number,
            customer_email__iexact=customer_email,
        ).first()
    except DatabaseError:
        return {
            "success": False,
            "error": "Order lookup is temporarily unavailable.",
        }

    if order is None:
        return {
            "success": False,
            "error": "No matching order was found. Please verify your details.",
        }

    return {
        "success": True,
        "order_number": order.order_number,
        "status": order.status,
        "total_amount": str(order.total_amount),
    }

#uses keyword matching 
def search_faq(query: str) -> dict:
    """
    Search active FAQ entries using basic keyword matching.
    """
    query = query.strip().lower()

    if not query:
        return {
            "success": False,
            "error": "A search query is required.",
        }

    try:
        faqs = list(
            FAQEntry.objects.filter(is_active=True).values(
                "question",
                "answer",
                "category",
            )
        )
    except DatabaseError:
        return {
            "success": False,
            "error": "FAQ search is temporarily unavailable.",
        }

    keywords = set(query.split())
    matches = []

    for faq in faqs:
        searchable_text = (
            f"{faq['question']} {faq['category']}"
        ).lower()

        score = sum(
            1 for word in keywords if word in searchable_text
        )

        if score > 0:
            matches.append((score, faq))

    matches.sort(key=lambda item: item[0], reverse=True)

    if not matches:
        return {
            "success": False,
            "error": "No relevant FAQ was found.",
        }

    return {
        "success": True,
        "results": [faq for _, faq in matches[:3]],
    }


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