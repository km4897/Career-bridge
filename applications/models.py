from django.conf import settings
from django.db import models

from opportunities.models import Opportunity


class Application(models.Model):
    class Status(models.TextChoices):
        APPLIED = "APPLIED", "Applied"
        UNDER_REVIEW = "UNDER_REVIEW", "Under Review"
        SHORTLISTED = "SHORTLISTED", "Shortlisted"
        INTERVIEW = "INTERVIEW", "Interview"
        ACCEPTED = "ACCEPTED", "Accepted"
        REJECTED = "REJECTED", "Rejected"

    applicant = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="applications",
        limit_choices_to={"role": "APPLICANT"},
    )
    opportunity = models.ForeignKey(
        Opportunity, on_delete=models.CASCADE, related_name="applications"
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPLIED)

    # Per-application details — deliberately separate from ApplicantProfile
    # so someone can tailor their name/phone/CV for a specific vacancy
    # instead of always reusing their generic profile info. All optional:
    # if left blank, the profile's version is used as a fallback wherever
    # this is displayed.
    full_name = models.CharField(max_length=150, blank=True, help_text="Leave blank to use your profile name")
    phone_number = models.CharField(max_length=20, blank=True, help_text="Leave blank to use your profile phone number")
    cv = models.FileField(upload_to="application_cvs/", blank=True, null=True, help_text="Leave blank to use your profile CV")
    cover_note = models.TextField(blank=True)

    submitted_at = models.DateTimeField(auto_now_add=True)
    decision_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-submitted_at"]
        unique_together = ("applicant", "opportunity")

    def __str__(self):
        return f"{self.applicant} -> {self.opportunity} ({self.get_status_display()})"

    def display_name(self):
        return self.full_name or self.applicant.username

    def display_cv(self):
        """The CV to show for this application: the one uploaded
        specifically for this vacancy, or the applicant's profile CV."""
        if self.cv:
            return self.cv
        profile = getattr(self.applicant, "applicant_profile", None)
        return profile.cv if profile and profile.cv else None
