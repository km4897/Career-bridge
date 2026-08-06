from django.conf import settings
from django.db import models


class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ApplicantProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applicant_profile",
        limit_choices_to={"role": "APPLICANT"},
    )
    full_name = models.CharField(max_length=150, blank=True)
    bio = models.TextField(blank=True)
    education = models.CharField(max_length=255, blank=True, help_text="e.g. BSc Computer Science, Makerere University")
    skills = models.ManyToManyField(Skill, blank=True, related_name="applicants")

    cv = models.FileField(upload_to="cvs/", blank=True, null=True)
    certificate = models.FileField(upload_to="certificates/", blank=True, null=True)
    id_document = models.FileField(upload_to="ids/", blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.full_name or self.user.username


class EmployerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="employer_profile",
        limit_choices_to={"role": "EMPLOYER"},
    )
    organisation_name = models.CharField(max_length=200, blank=True)
    sector = models.CharField(max_length=120, blank=True)
    description = models.TextField(blank=True)
    logo = models.ImageField(upload_to="logos/", blank=True, null=True)
    website = models.URLField(blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.organisation_name or self.user.username
