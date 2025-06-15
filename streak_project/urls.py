from django.contrib import admin
from django.urls import path, include
from users import views as user_views
from core import views as core_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", user_views.register, name="register"),
    path("login/", user_views.user_login, name="login"),
    path("logout/", user_views.user_logout, name="logout"),
    path("", core_views.home, name="home"),
    path("reports/", core_views.reports, name="reports"),
    path("profile/", core_views.profile, name="profile"),
]
