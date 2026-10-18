
from support.models import Conversation, Message


def get_or_create_conversation(
    customer_email: str,
    conversation_id: str = None,
) -> Conversation:
    """Retrieve an existing customer conversation or create a new one."""

    if conversation_id:
        return Conversation.objects.get(
            id=conversation_id,
            customer_email__iexact=customer_email,
        )

    return Conversation.objects.create(
        customer_email=customer_email,
    )


def save_message(
    conversation: Conversation,
    role: str,
    content: str,
) -> Message:
    """Save a message to the conversation."""

    return Message.objects.create(
        conversation=conversation,
        role=role,
        content=content,
    )
