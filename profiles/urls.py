from django.urls import path
from . import views

app_name = "profiles"

urlpatterns = [
    path("applicant/edit/", views.edit_applicant_profile, name="edit_applicant"),
    path("employer/edit/", views.edit_employer_profile, name="edit_employer"),
]
