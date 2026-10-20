
from unittest.mock import patch

from django.core.cache import cache
from django.test import override_settings
from rest_framework.test import APITestCase


@override_settings(
    REST_FRAMEWORK={
        "DEFAULT_THROTTLE_RATES": {
            "chat": "20/hour",
        }
    }
)
class ChatThrottlingTests(APITestCase):

    def setUp(self):
        cache.clear()

    def tearDown(self):
        cache.clear()

    @patch("support.views.chat.chat_view.run_agent")
    def test_chat_returns_429_after_rate_limit(self, mock_run_agent):
        mock_run_agent.return_value = {
            "response": "Test response",
            "conversation_id": "test-conversation",
            "latency_seconds": 0.01,
            "tools_used": [],
        }

        payload = {
            "customer_email": "customer@example.com",
            "message": "Hello",
        }

        for _ in range(20):
            response = self.client.post(
                "/api/chat/",
                payload,
                format="json",
                REMOTE_ADDR="192.0.2.10",
            )
            self.assertEqual(response.status_code, 200)

        response = self.client.post(
            "/api/chat/",
            payload,
            format="json",
            REMOTE_ADDR="192.0.2.10",
        )

        self.assertEqual(response.status_code, 429)
        self.assertEqual(mock_run_agent.call_count, 20)
