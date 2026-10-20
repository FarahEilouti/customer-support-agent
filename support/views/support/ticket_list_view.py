from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication

from support.models import SupportTicket
from support.serializers.ticket_serializer import TicketSerializer


class TicketListAPIView(APIView):
    """
    GET /api/tickets/

    Return all support tickets for staff users.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request):
        tickets = SupportTicket.objects.all()

        serializer = TicketSerializer(
            tickets,
            many=True,
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )
