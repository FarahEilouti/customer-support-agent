from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.authentication import SessionAuthentication

from support.models import SupportTicket
from support.serializers.ticket_serializer import (
    TicketSerializer,
    TicketUpdateSerializer,
)


class TicketDetailAPIView(APIView):
    """
    GET /api/tickets/<id>/
    PATCH /api/tickets/<id>/

    View or update a support ticket.
    """

    authentication_classes = [SessionAuthentication]
    permission_classes = [IsAdminUser]

    def get_object(self, ticket_id):
        return get_object_or_404(
            SupportTicket,
            id=ticket_id,
        )

    def get(self, request, ticket_id):
        ticket = self.get_object(ticket_id)

        serializer = TicketSerializer(ticket)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK,
        )

    def patch(self, request, ticket_id):
        ticket = self.get_object(ticket_id)

        serializer = TicketUpdateSerializer(
            data=request.data,
        )

        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            setattr(ticket, field, value)

        ticket.save()

        response_serializer = TicketSerializer(ticket)

        return Response(
            response_serializer.data,
            status=status.HTTP_200_OK,
        )
