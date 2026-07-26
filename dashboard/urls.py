from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.redirect_dashboard, name="redirect"),
    path("applicant/", views.applicant_dashboard, name="applicant"),
    path("employer/", views.employer_dashboard, name="employer"),
    path("admin/", views.admin_dashboard, name="admin"),
]
