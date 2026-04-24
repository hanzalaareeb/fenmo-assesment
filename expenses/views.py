from decimal import Decimal

from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Expense, IdempotencyKey
from .serializers import ExpenseSerializer


def index(request):
    return render(request, "expenses/index.html")


class ExpenseListCreateView(APIView):

    def get(self, request):
        """
        GET api/exepnses/
        
        """
        qs = Expense.objects.all()

        category = request.query_params.get("category")
        if category:
            qs = qs.filter(category__iexact=category)

        sort = request.query_params.get("sort")
        if sort == "date_asc":
            qs = qs.order_by("date", "created_at")
        elif sort == "date_desc":
            qs = qs.order_by("-date", "-created_at")

        serializer = ExpenseSerializer(qs, many=True)
        total = qs.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")

        return Response({
            "expenses": serializer.data,
            "total": f"{total:.2f}",
        })

    def post(self, request):
        """
        POST api/expenses/
        request body:
            amount,
            category,
            description,
            date,
        """
        idempotency_key = request.headers.get("Idempotency-Key")

        if idempotency_key:
            try:
                existing = IdempotencyKey.objects.get(key=idempotency_key)
                return Response(
                    ExpenseSerializer(existing.expense).data,
                    status=status.HTTP_200_OK,
                )

            except IdempotencyKey.DoesNotExist:
                pass

        serializer = ExpenseSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic(): # adding atomic to idempotency
                expense = serializer.save()
                if idempotency_key:
                    IdempotencyKey.objects.create(key=idempotency_key, expense=expense)
        
        except IntegrityError:
            existing = IdempotencyKey.objects.get(key=idempotency_key)
            return Response(
                ExpenseSerializer(existing.expense).data,
                status=status.HTTP_200_OK,
            )

        return Response(
            ExpenseSerializer(expense).data,
            status=status.HTTP_201_CREATED,
        )
