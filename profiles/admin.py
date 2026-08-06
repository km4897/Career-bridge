from django.contrib import admin
from .models import ApplicantProfile, EmployerProfile, Skill


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(ApplicantProfile)
class ApplicantProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "full_name", "education", "updated_at")
    filter_horizontal = ("skills",)
    search_fields = ("full_name", "user__username")


@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "organisation_name", "sector", "updated_at")
    search_fields = ("organisation_name", "user__username")
