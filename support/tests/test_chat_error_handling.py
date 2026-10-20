
from unittest.mock import patch

from django.test import TestCase
from rest_framework.test import APIClient


class ChatErrorHandlingTests(TestCase):

    @patch("support.views.chat.chat_view.run_agent")
    def test_unexpected_error_returns_503(self, mock_run_agent):
        """Unexpected errors should return a safe response."""

        mock_run_agent.side_effect = RuntimeError(
            "Internal service failure"
        )

        client = APIClient()

        response = client.post(
            "/api/chat/",
            {
                "customer_email": "customer@example.com",
                "message": "Hello!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 503)

        self.assertEqual(
            response.data["error"],
            "The service is temporarily unavailable. Please try again later.",
        )

        self.assertNotIn(
            "Internal service failure",
            str(response.data),
        )
