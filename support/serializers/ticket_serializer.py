
from rest_framework import serializers

from support.models import SupportTicket


class TicketSerializer(serializers.ModelSerializer):
    conversation_id = serializers.UUIDField(read_only=True)

    class Meta:
        model = SupportTicket
        fields = [
            "id",
            "conversation_id",
            "title",
            "description",
            "customer_email",
            "status",
            "priority",
            "created_at",
            "updated_at",
        ]
        read_only_fields = fields


class TicketUpdateSerializer(serializers.Serializer):
    status = serializers.ChoiceField(
        choices=SupportTicket.Status.choices,
        required=False,
    )

    priority = serializers.ChoiceField(
        choices=SupportTicket.Priority.choices,
        required=False,
    )

    def validate(self, attrs):
        if not attrs:
            raise serializers.ValidationError(
                "Provide status or priority to update."
            )

        return attrs
