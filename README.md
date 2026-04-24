# Expense Tracker

 expense tracking application

## Quick Start

```bash
uv sync
uv run python manage.py migrate
uv run python manage.py runserver
```

## API Endpoints

### POST /api/expenses

Create a new expense. Accepts an optional `Idempotency-Key` header to prevent duplicate creation on retries.

**Request body:** `{ "amount", "category", "description", "date" }`

### GET /api/expenses

List expenses. Returns `{ "expenses": [...], "total": "150.00" }`.

**Query params:**
- `category` — filter by category
- `sort=date_asc` — sort oldest first

## Running Tests

```bash
uv run python manage.py test expenses
```

## Design Decisions

- Idempotency: POST accepts an `Idempotency-Key` header. The server stores the key in an `IdempotencyKey` table linked to the created expense. Duplicate requests return the original expense. The unique constraint + `transaction.atomic()` handles race conditions.
- SQLite: Sufficient for this scope. Easy to set up, no external dependencies.
- Vanilla JS frontend: Single HTML template with no build step.

## What I Intentionally Did Not Do

- Auth & User Managment: It would take time, and add too many debugging steps. Will add it in later iterations,
- Async Tasks: No heavy task processing requires,
- Full Idempotency Persistence: Overkill for the scope.
- Complex UI/UX:
