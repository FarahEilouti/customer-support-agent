
from unittest.mock import MagicMock, patch

from django.test import TestCase
from google.genai.errors import ClientError

from support.models import AgentAction, Message, SupportTicket
from support.services.agent_service import run_agent


class AgentReliabilityTests(TestCase):

    def setUp(self):
        self.email = "customer@example.com"

    @patch("support.services.agent_service.genai.Client")
    def test_ticket_confirmation_when_gemini_fails(self, mock_client):
        """
        A ticket is created, then Gemini fails.
        The customer should still receive the ticket confirmation.
        """

        def simulate_gemini_request(message):
            # Simulate Gemini calling the registered ticket tool.
            config = mock_client.return_value.chats.create.call_args.kwargs[
                "config"
            ]
            ticket_tool = config.tools[2]

            ticket_tool(
                title="Damaged product",
                description="The product arrived damaged.",
                priority="high",
            )

            # Simulate Gemini failing after the tool completed.
            raise ClientError(
                429,
                {"error": {"message": "Quota exceeded"}},
            )

        mock_chat = mock_client.return_value.chats.create.return_value
        mock_chat.send_message.side_effect = simulate_gemini_request

        result = run_agent(
            customer_email=self.email,
            user_message="Please create a ticket for my damaged product.",
        )

        self.assertEqual(SupportTicket.objects.count(), 1)

        ticket = SupportTicket.objects.get()

        self.assertIn(str(ticket.id), result["response"])
        self.assertIn("created successfully", result["response"])
        self.assertIn("create_support_ticket", result["tools_used"])

        self.assertTrue(
            AgentAction.objects.filter(
                conversation=ticket.conversation,
                tool_name="create_support_ticket",
                success=True,
            ).exists()
        )

        self.assertTrue(
            Message.objects.filter(
                conversation=ticket.conversation,
                role=Message.Role.ASSISTANT,
            ).exists()
        )

    @patch("support.services.agent_service.genai.Client")
    def test_api_failure_without_ticket_is_raised(self, mock_client):
        """
        Gemini fails before executing any tool.
        The system must not claim that a ticket was created.
        """

        mock_chat = mock_client.return_value.chats.create.return_value

        mock_chat.send_message.side_effect = ClientError(
            429,
            {"error": {"message": "Quota exceeded"}},
        )

        with self.assertRaises(ClientError):
            run_agent(
                customer_email=self.email,
                user_message="Hello!",
            )

        self.assertEqual(SupportTicket.objects.count(), 0)
        self.assertEqual(AgentAction.objects.count(), 0)
