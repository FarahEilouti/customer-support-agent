from django.db import models

from .conversation import Conversation


class Message(models.Model):

    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.role}: {self.content[:50]}"

    class Meta:
        ordering = ["created_at", "id"]

# foreignkey, each message belongs to a conversation,
#  and a conversation can have many messages.
#  The related_name="messages" allows us to access all messages of a conversation using conversation.messages.all().