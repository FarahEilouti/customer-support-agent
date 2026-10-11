from django.db import models

from .conversation import Conversation


class SupportTicket(models.Model):

    class Status(models.TextChoices):
        OPEN = "open", "Open"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"

    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.PROTECT, #so that conversations cannot be deleted if they have associated support tickets
        related_name="tickets",
    )

    title = models.CharField(max_length=200)

    description = models.TextField()

    customer_email = models.EmailField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
    )

    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Ticket #{self.id}: {self.title}"

    class Meta:
        ordering = ["-created_at"]