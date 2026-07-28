from django.contrib import admin
from .models import Opportunity


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ("title", "employer", "opportunity_type", "location", "is_active", "created_at")
    list_filter = ("opportunity_type", "is_active", "location")
    search_fields = ("title", "description", "skills_required")
    prepopulated_fields = {"slug": ("title",)}
