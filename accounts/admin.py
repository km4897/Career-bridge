from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User


class CareerBridgeUserAdmin(UserAdmin):
    list_display = ("username", "email", "role", "is_verified", "is_staff")
    list_filter = ("role", "is_verified", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("CareerBridge Profile", {"fields": ("role", "is_verified", "phone_number")}),
    )


admin.site.register(User, CareerBridgeUserAdmin)
