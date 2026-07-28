from django.urls import path
from . import views

app_name = "applications"

urlpatterns = [
    path("mine/", views.my_applications, name="my_applications"),
    path("apply/<slug:slug>/", views.apply_to_opportunity, name="apply"),
    path("for/<slug:slug>/", views.opportunity_applicants, name="opportunity_applicants"),
    path("<int:pk>/status/", views.update_application_status, name="update_status"),
]
