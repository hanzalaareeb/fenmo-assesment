import uuid
from django.db import models

class Expense(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Monetary amount (e.g., 1234.50)")
    category = models.CharField(max_length=100, db_index=True)
    description = models.TextField(blank=True)
    date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date", "-created_at"]  # newest first by default
        indexes = [
            models.Index(fields=["category"]),
            models.Index(fields=["date"]),
        ]

    def __str__(self):
        return f"{self.category} - ₹{self.amount} on {self.date}"