from django.urls import path
from . import views

app_name = "opportunities"

urlpatterns = [
    path("", views.opportunity_list, name="list"),
    path("mine/", views.my_opportunities, name="my_opportunities"),
    path("new/", views.opportunity_create, name="create"),
    path("<slug:slug>/", views.opportunity_detail, name="detail"),
    path("<slug:slug>/edit/", views.opportunity_update, name="update"),
    path("<slug:slug>/delete/", views.opportunity_delete, name="delete"),
]
