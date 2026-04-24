from datetime import date

from rest_framework import serializers
from .models import Expense


class ExpenseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Expense
        fields = ["id", "amount", "category", "description", "date", "created_at"]
        read_only_fields = ["id", "created_at"]

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("Amount must be positive.")
        return value

    def validate_date(self, value): # no future date, validation for future date
        if value > date.today():
            raise serializers.ValidationError("Date cannot be in the future.")
        return value
