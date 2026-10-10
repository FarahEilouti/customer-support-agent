from django.db import models


class FAQEntry(models.Model):

    class Category(models.TextChoices):
        SHIPPING = "shipping", "Shipping"
        RETURNS = "returns", "Returns"
        REFUNDS = "refunds", "Refunds"
        GENERAL = "general", "General"

    question = models.CharField(max_length=255)

    answer = models.TextField()

    category = models.CharField(
        max_length=20,
        choices=Category.choices,
        default=Category.GENERAL,
    )

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.question

    class Meta:
        ordering = ["category", "question"]