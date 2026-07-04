import csv
import json
from collections import defaultdict

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.core.paginator import Paginator
from django.db.models import Avg, Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from .forms import ExpenseForm
from .models import Category, Expense

def home(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return render(request, "expenses/home.html")


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    if request.method == "POST":
        form = UserCreationForm(request.POST)

        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully.")
            return redirect("dashboard")
    else:
        form = UserCreationForm()

    return render(
        request,
        "registration/register.html",
        {"form": form},
    )


@login_required
def dashboard(request):

    expenses = Expense.objects.filter(
        student=request.user
    ).select_related("category")

    search = request.GET.get("search", "")
    category = request.GET.get("category", "")
    from_date = request.GET.get("from_date", "")
    to_date = request.GET.get("to_date", "")

    if search:
        expenses = expenses.filter(
            Q(title__icontains=search)
            |
            Q(description__icontains=search)
            |
            Q(category__name__icontains=search)
        )

    if category:
        expenses = expenses.filter(category_id=category)

    if from_date:
        expenses = expenses.filter(expense_date__gte=from_date)

    if to_date:
        expenses = expenses.filter(expense_date__lte=to_date)

    total_expense = expenses.aggregate(
        total=Sum("amount")
    )["total"] or 0

    total_records = expenses.count()

    average_expense = expenses.aggregate(
        avg=Avg("amount")
    )["avg"] or 0

    category_count = Category.objects.count()

    monthly_totals = defaultdict(float)
    category_totals = defaultdict(float)

    for expense in expenses:
        month = expense.expense_date.strftime("%b")
        monthly_totals[month] += float(expense.amount)
        category_totals[expense.category.name] += float(expense.amount)

    paginator = Paginator(
        expenses.order_by("-expense_date", "-created_at"),
        10,
    )

    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "expenses": page_obj,
        "page_obj": page_obj,
        "recent_expenses": expenses.order_by("-created_at")[:5],
        "categories": Category.objects.all(),
        "selected_category": category,
        "search": search,
        "from_date": from_date,
        "to_date": to_date,
        "total_expense": total_expense,
        "total_records": total_records,
        "average_expense": round(average_expense, 2),
        "category_count": category_count,
        "chart_labels": json.dumps(list(monthly_totals.keys())),
        "chart_values": json.dumps(list(monthly_totals.values())),
        "pie_labels": json.dumps(list(category_totals.keys())),
        "pie_values": json.dumps(list(category_totals.values())),
    }

    return render(
        request,
        "expenses/dashboard.html",
        context,
    )


@login_required
def export_csv(request):

    expenses = Expense.objects.filter(
        student=request.user
    ).select_related("category")

    search = request.GET.get("search", "")
    category = request.GET.get("category", "")
    from_date = request.GET.get("from_date", "")
    to_date = request.GET.get("to_date", "")

    if search:
        expenses = expenses.filter(
            Q(title__icontains=search)
            | Q(description__icontains=search)
            | Q(category__name__icontains=search)
        )

    if category:
        expenses = expenses.filter(category_id=category)

    if from_date:
        expenses = expenses.filter(expense_date__gte=from_date)

    if to_date:
        expenses = expenses.filter(expense_date__lte=to_date)

    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="expenses.csv"'

    writer = csv.writer(response)

    writer.writerow([
        "Title",
        "Category",
        "Amount",
        "Date",
        "Description",
    ])

    for expense in expenses:

        writer.writerow([
            expense.title,
            expense.category.name,
            expense.amount,
            expense.expense_date,
            expense.description,
        ])

    return response

@login_required
def profile(request):

    expenses = Expense.objects.filter(student=request.user)

    context = {
        "user": request.user,
        "total_expenses": expenses.count(),
        "total_amount": expenses.aggregate(
            total=Sum("amount")
        )["total"] or 0,
    }

    return render(
        request,
        "expenses/profile.html",
        context,
    )

@login_required
def add_expense(request):

    if request.method == "POST":

        form = ExpenseForm(request.POST)

        if form.is_valid():

            expense = form.save(commit=False)
            expense.student = request.user
            expense.save()

            messages.success(
                request,
                "Expense added successfully.",
            )

            return redirect("dashboard")

    else:

        form = ExpenseForm()

    return render(
        request,
        "expenses/add_expense.html",
        {
            "form": form,
        },
    )


@login_required
def edit_expense(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
        student=request.user,
    )

    if request.method == "POST":

        form = ExpenseForm(
            request.POST,
            instance=expense,
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Expense updated successfully.",
            )

            return redirect("dashboard")

    else:

        form = ExpenseForm(instance=expense)

    return render(
        request,
        "expenses/edit_expense.html",
        {
            "form": form,
            "expense": expense,
        },
    )


@login_required
def delete_expense(request, pk):

    expense = get_object_or_404(
        Expense,
        pk=pk,
        student=request.user,
    )

    if request.method == "POST":

        expense.delete()

        messages.success(
            request,
            "Expense deleted successfully.",
        )

        return redirect("dashboard")

    return render(
        request,
        "expenses/delete_expense.html",
        {
            "expense": expense,
        },
    )