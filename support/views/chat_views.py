import logging

from django.core.exceptions import ObjectDoesNotExist
from google.genai.errors import APIError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from support.serializers.chat_serializer import ChatRequestSerializer
from support.services.agent_service import run_agent
from rest_framework.throttling import AnonRateThrottle

logger = logging.getLogger(__name__)

class ChatRateThrottle(AnonRateThrottle):
    scope = "chat"
class ChatAPIView(APIView):

    throttle_classes = [ChatRateThrottle]

    def post(self, request):
        serializer = ChatRequestSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data

        try:
            result = run_agent(
                customer_email=data["customer_email"],
                user_message=data["message"],
                conversation_id=(
                    str(data["conversation_id"])
                    if data.get("conversation_id")
                    else None
                ),
            )

            return Response(result, status=status.HTTP_200_OK)

        except ObjectDoesNotExist:
            return Response(
                {"error": "Conversation not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        except ValueError as exc:
            return Response(
                {"error": str(exc)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        except APIError:
            logger.exception("Gemini API error")
            return Response(
                {"error": "AI service is temporarily unavailable."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        except Exception:
            logger.exception("Unexpected error while processing chat request")
            return Response(
                {
                    "error": "The service is temporarily unavailable. Please try again later."
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )