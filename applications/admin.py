from django.contrib import admin
from .models import Application


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("applicant", "opportunity", "status", "submitted_at")
    list_filter = ("status",)
    search_fields = ("applicant__username", "opportunity__title")
