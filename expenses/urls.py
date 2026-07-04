from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    path("profile/", views.profile, name="profile"),

    path("add/", views.add_expense, name="add_expense"),

    path("edit/<int:pk>/", views.edit_expense, name="edit_expense"),

    path("delete/<int:pk>/", views.delete_expense, name="delete_expense"),

    path("export/csv/", views.export_csv, name="export_csv"),
]