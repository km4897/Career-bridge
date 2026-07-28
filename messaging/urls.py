from django.urls import path
from . import views

app_name = "messaging"

urlpatterns = [
    path("<int:application_id>/", views.thread, name="thread"),
]
