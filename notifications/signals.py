"""
Signal handlers that create Notification records from events in other
apps (applications). Wired up in NotificationsConfig.ready().
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from applications.models import Application

from .models import Notification


@receiver(post_save, sender=Application)
def notify_on_application_change(sender, instance, created, **kwargs):
    if created:
        # New application -> notify the employer who owns the opportunity.
        Notification.objects.create(
            recipient=instance.opportunity.employer,
            message=f"{instance.applicant.username} applied to '{instance.opportunity.title}'.",
            link=f"/applications/for/{instance.opportunity.slug}/",
        )
    else:
        # Status change -> notify the applicant.
        Notification.objects.create(
            recipient=instance.applicant,
            message=f"Your application to '{instance.opportunity.title}' is now: {instance.get_status_display()}.",
            link="/applications/mine/",
        )
