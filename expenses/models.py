import uuid
from django.db import models

class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monetary amount") # using DecimalField for money
    category = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]  # newest first by default
        indexes = [
            # centerized indexing
            models.Index(fields=["category"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"{self.category} - ₹{self.amount} on {self.date}"


class IdempotencyKey(models.Model):
    # Adding Idempotency
    key = models.CharField(max_length=255, unique=True)
    expense = models.ForeignKey(Expense, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)