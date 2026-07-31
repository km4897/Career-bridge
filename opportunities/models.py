from datetime import timedelta

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify


class Opportunity(models.Model):
    class Type(models.TextChoices):
        INTERNSHIP = "INTERNSHIP", "Internship"
        APPRENTICESHIP = "APPRENTICESHIP", "Apprenticeship"
        VOLUNTEER = "VOLUNTEER", "Volunteer"

    employer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="opportunities",
        limit_choices_to={"role": "EMPLOYER"},
    )
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    description = models.TextField()
    opportunity_type = models.CharField(max_length=20, choices=Type.choices, default=Type.INTERNSHIP)
    location = models.CharField(max_length=120)
    duration_weeks = models.PositiveIntegerField(help_text="Duration in weeks")

    # Simple comma-separated skills for now. Once the `profiles` app ships
    # a proper Skill model, this can be migrated to a ManyToManyField.
    skills_required = models.CharField(
        max_length=300, blank=True,
        help_text="Comma-separated, e.g. Python, Django, Communication"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "Opportunities"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)[:200]
            slug = base_slug
            counter = 1
            while Opportunity.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("opportunities:detail", kwargs={"slug": self.slug})

    def skills_list(self):
        return [s.strip() for s in self.skills_required.split(",") if s.strip()]

    @property
    def expires_at(self):
        """The moment this posting is considered expired, based on when
        it was created plus its stated duration."""
        return self.created_at + timedelta(weeks=self.duration_weeks)

    @property
    def is_expired(self):
        return timezone.now() >= self.expires_at

    @property
    def days_remaining(self):
        """Whole days left before expiry; 0 if already expired."""
        delta = self.expires_at - timezone.now()
        return max(delta.days, 0)
