from rest_framework import serializers


class ChatRequestSerializer(serializers.Serializer):
    customer_email = serializers.EmailField()
    message = serializers.CharField(
        allow_blank=False,
        trim_whitespace=True,
        max_length=5000,
    )
    conversation_id = serializers.UUIDField(required=False)