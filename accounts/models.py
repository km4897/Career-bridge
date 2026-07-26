from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom user model for CareerBridge.
    Adds a `role` field so the same login system serves Applicants,
    Employers, and Administrators, with role-based access control
    enforced in views/permissions.
    """

    class Role(models.TextChoices):
        APPLICANT = "APPLICANT", "Applicant"
        EMPLOYER = "EMPLOYER", "Employer"
        ADMIN = "ADMIN", "Administrator"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.APPLICANT)
    is_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"

    @property
    def is_applicant(self):
        return self.role == self.Role.APPLICANT

    @property
    def is_employer(self):
        return self.role == self.Role.EMPLOYER

    @property
    def is_admin_role(self):
        return self.role == self.Role.ADMIN
