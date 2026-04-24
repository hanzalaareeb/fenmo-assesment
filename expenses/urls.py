from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("api/expenses", views.ExpenseListCreateView.as_view(), name="expense-list-create"),
]
