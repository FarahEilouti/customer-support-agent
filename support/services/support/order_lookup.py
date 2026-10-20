from django.db import DatabaseError
from support.models import Order


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
