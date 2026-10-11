from django.db import models

from .conversation import Conversation


class AgentAction(models.Model):

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="agent_actions",
    )

    tool_name = models.CharField(max_length=100)

    arguments = models.JSONField(default=dict)

    result = models.JSONField(default=dict)

    success = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.tool_name} - {'Success' if self.success else 'Failed'}"

    class Meta:
        ordering = ["-created_at"]