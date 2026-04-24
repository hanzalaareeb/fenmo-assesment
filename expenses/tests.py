import uuid
from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APIClient

from .models import Expense


class ExpenseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.valid_payload = {
            "amount": "50.00",
            "category": "Food",
            "description": "Lunch",
            "date": "2026-04-20",
        }

    # --- POST ---

    def test_create_expense(self):
        resp = self.client.post("/api/expenses", self.valid_payload, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(Expense.objects.count(), 1)
        expense = Expense.objects.first()
        self.assertEqual(expense.category, "Food")
        self.assertEqual(expense.amount, Decimal("50.00"))

    def test_reject_negative_amount(self):
        payload = {**self.valid_payload, "amount": "-10.00"}
        resp = self.client.post("/api/expenses", payload, format="json")
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(Expense.objects.count(), 0)

    def test_reject_zero_amount(self):
        payload = {**self.valid_payload, "amount": "0.00"}
        resp = self.client.post("/api/expenses", payload, format="json")
        self.assertEqual(resp.status_code, 400)

    def test_reject_missing_date(self):
        payload = {**self.valid_payload}
        del payload["date"]
        resp = self.client.post("/api/expenses", payload, format="json")
        self.assertEqual(resp.status_code, 400)

    # --- Idempotency ---

    def test_idempotency_same_key_creates_one_expense(self):
        key = str(uuid.uuid4())
        resp1 = self.client.post(
            "/api/expenses", self.valid_payload, format="json",
            HTTP_IDEMPOTENCY_KEY=key,
        )
        resp2 = self.client.post(
            "/api/expenses", self.valid_payload, format="json",
            HTTP_IDEMPOTENCY_KEY=key,
        )
        self.assertEqual(resp1.status_code, 201)
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(Expense.objects.count(), 1)
        self.assertEqual(resp1.json()["id"], resp2.json()["id"])

    def test_different_keys_create_separate_expenses(self):
        self.client.post(
            "/api/expenses", self.valid_payload, format="json",
            HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
        )
        self.client.post(
            "/api/expenses", self.valid_payload, format="json",
            HTTP_IDEMPOTENCY_KEY=str(uuid.uuid4()),
        )
        self.assertEqual(Expense.objects.count(), 2)

    # --- GET ---

    def test_list_expenses_with_total(self):
        Expense.objects.create(amount=Decimal("10.00"), category="Food", date="2026-04-20")
        Expense.objects.create(amount=Decimal("20.00"), category="Transport", date="2026-04-21")
        resp = self.client.get("/api/expenses")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(len(data["expenses"]), 2)
        self.assertEqual(data["total"], "30.00")

    def test_filter_by_category(self):
        Expense.objects.create(amount=Decimal("10.00"), category="Food", date="2026-04-20")
        Expense.objects.create(amount=Decimal("20.00"), category="Transport", date="2026-04-21")
        resp = self.client.get("/api/expenses?category=Food")
        data = resp.json()
        self.assertEqual(len(data["expenses"]), 1)
        self.assertEqual(data["total"], "10.00")

    def test_default_sort_newest_first(self):
        Expense.objects.create(amount=Decimal("10.00"), category="Food", date="2026-04-20")
        Expense.objects.create(amount=Decimal("20.00"), category="Food", date="2026-04-22")
        resp = self.client.get("/api/expenses")
        dates = [e["date"] for e in resp.json()["expenses"]]
        self.assertEqual(dates, ["2026-04-22", "2026-04-20"])

    def test_sort_ascending(self):
        Expense.objects.create(amount=Decimal("10.00"), category="Food", date="2026-04-20")
        Expense.objects.create(amount=Decimal("20.00"), category="Food", date="2026-04-22")
        resp = self.client.get("/api/expenses?sort=date_asc")
        dates = [e["date"] for e in resp.json()["expenses"]]
        self.assertEqual(dates, ["2026-04-20", "2026-04-22"])
