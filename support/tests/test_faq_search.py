
from django.test import TestCase

from support.models import FAQEntry
from support.services.support_tools import search_faq


class FAQSearchTests(TestCase):

    def test_search_matches_answer_content(self):
        FAQEntry.objects.create(
            question="Delivery information",
            answer="Tracking is available after dispatch.",
            category="shipping",
            is_active=True,
        )

        result = search_faq("tracking")

        self.assertTrue(result["success"])
        self.assertEqual(
            result["results"][0]["question"],
            "Delivery information",
        )

    def test_search_uses_whole_words(self):
        FAQEntry.objects.create(
            question="Shipping information",
            answer="Delivery details",
            category="shipping",
            is_active=True,
        )

        result = search_faq("ship")

        self.assertFalse(result["success"])

    def test_inactive_faq_is_excluded(self):
        FAQEntry.objects.create(
            question="Warranty policy",
            answer="Warranty coverage details",
            category="general",
            is_active=False,
        )

        result = search_faq("warranty")

        self.assertFalse(result["success"])

    def test_stop_words_do_not_create_matches(self):
        FAQEntry.objects.create(
            question="How is the delivery arranged?",
            answer="Delivery information",
            category="shipping",
            is_active=True,
        )

        result = search_faq("how is the")

        self.assertFalse(result["success"])

    def test_question_matches_rank_above_answer_matches(self):
        FAQEntry.objects.create(
            question="General information",
            answer="Tracking instructions",
            category="general",
            is_active=True,
        )

        FAQEntry.objects.create(
            question="Tracking information",
            answer="Delivery information",
            category="shipping",
            is_active=True,
        )

        result = search_faq("tracking")

        self.assertTrue(result["success"])
        self.assertEqual(
            result["results"][0]["question"],
            "Tracking information",
        )
