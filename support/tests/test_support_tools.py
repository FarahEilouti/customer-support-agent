
from django.test import TestCase

from support.models import (
    Order,
    FAQEntry,
    Conversation,
    SupportTicket,
)

from support.services.support_tools import (
    lookup_order,
    search_faq,
    create_support_ticket,
)


class OrderToolTests(TestCase):

    def setUp(self):
        Order.objects.create(
            order_number="ORD-TEST-100",
            customer_email="test@example.com",
            status="shipped",
            total_amount="45.50",
        )

    def test_lookup_existing_order(self):
        result = lookup_order(
            "ORD-TEST-100",
            "test@example.com",
        )

        self.assertTrue(result["success"])
        self.assertEqual(result["status"], "shipped")
        self.assertEqual(
            result["order_number"],
            "ORD-TEST-100",
        )

    def test_lookup_order_with_wrong_email(self):
        result = lookup_order(
            "ORD-TEST-100",
            "wrong@example.com",
        )

        self.assertFalse(result["success"])

    def test_lookup_nonexistent_order(self):
        result = lookup_order(
            "ORD-UNKNOWN",
            "test@example.com",
        )

        self.assertFalse(result["success"])


class FAQToolTests(TestCase):

    def setUp(self):
        FAQEntry.objects.create(
            question="How long does shipping take?",
            answer="Shipping takes 3 to 5 business days.",
            category="shipping",
            is_active=True,
        )

    def test_search_existing_faq(self):
        result = search_faq("shipping")

        self.assertTrue(result["success"])
        self.assertGreater(len(result["results"]), 0)

    def test_search_unknown_faq(self):
        result = search_faq(
            "quantum astronomy telescope"
        )

        self.assertFalse(result["success"])


class TicketToolTests(TestCase):

    def setUp(self):
        self.conversation = Conversation.objects.create(
            customer_email="test@example.com"
        )

    def test_create_ticket(self):
        result = create_support_ticket(
            conversation_id=str(self.conversation.id),
            title="Delayed order",
            description="My order has not arrived.",
            priority="high",
        )

        self.assertTrue(result["success"])

        ticket = SupportTicket.objects.get(
            id=result["ticket_id"]
        )

        self.assertEqual(ticket.priority, "high")
        self.assertEqual(ticket.status, "open")
        self.assertEqual(
            ticket.customer_email,
            "test@example.com",
        )

    def test_invalid_priority(self):
        result = create_support_ticket(
            conversation_id=str(self.conversation.id),
            title="Delayed order",
            description="My order has not arrived.",
            priority="urgent",
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            SupportTicket.objects.count(),
            0,
        )

    def test_empty_ticket_title(self):
        result = create_support_ticket(
            conversation_id=str(self.conversation.id),
            title="",
            description="My order has not arrived.",
        )

        self.assertFalse(result["success"])
        self.assertEqual(
            SupportTicket.objects.count(),
            0,
        )
