from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

from expenses import views

urlpatterns = [
    path("admin/", admin.site.urls),

    path("", views.home, name="home"),

    path("dashboard/", include("expenses.urls")),

    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),

    path(
        "logout/",
        auth_views.LogoutView.as_view(
            next_page="login"
        ),
        name="logout",
    ),

    path(
        "register/",
        views.register,
        name="register",
    ),

    path(
        "password/change/",
        auth_views.PasswordChangeView.as_view(
            template_name="registration/change_password.html",
            success_url="/dashboard/profile/"
        ),
        name="password_change",
    ),
]