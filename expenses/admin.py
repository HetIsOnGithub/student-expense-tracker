from django.contrib import admin
from .models import Category, Expense


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "title",
        "student",
        "category",
        "amount",
        "expense_date",
    )

    list_filter = (
        "category",
        "expense_date",
    )

    search_fields = (
        "title",
        "student__username",
    )

    ordering = (
        "-expense_date",
        "-created_at",
    )