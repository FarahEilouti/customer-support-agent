
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db import transaction

from support.models import Order, FAQEntry


class Command(BaseCommand):
    help = "Create sample orders and FAQ entries for a local demo."

    @transaction.atomic
    def handle(self, *args, **options):

        # Demo order
        order, created = Order.objects.update_or_create(
            order_number="ORD-1001",
            defaults={
                "customer_email": "customer@example.com",
                "status": Order.Status.SHIPPED,
                "total_amount": Decimal("45.50"),
            },
        )

        # Demo FAQ entries
        faqs = [
            {
                "question": "How long does standard shipping take?",
                "answer": (
                    "Standard shipping usually takes "
                    "3-5 business days."
                ),
                "category": FAQEntry.Category.SHIPPING,
            },
            {
                "question": "What is your return policy?",
                "answer": (
                    "For this demo, customers can request "
                    "a return within 14 days of delivery."
                ),
                "category": FAQEntry.Category.RETURNS,
            },
            {
                "question": "How can I get help with my order?",
                "answer": (
                    "You can ask the support assistant to "
                    "create a support ticket for human assistance."
                ),
                "category": FAQEntry.Category.GENERAL,
            },
        ]

        for faq_data in faqs:
            FAQEntry.objects.update_or_create(
                question=faq_data["question"],
                defaults={
                    "answer": faq_data["answer"],
                    "category": faq_data["category"],
                    "is_active": True,
                },
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Demo data is ready!\n"
                "Customer email: customer@example.com\n"
                "Order number: ORD-1001\n"
                "Order status: shipped\n"
                "FAQ entries: 3\n"
            )
        )
