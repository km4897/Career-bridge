"""
Rule-based recommendation engine (v1).

Scores active opportunities for a given applicant using signals we
already have: the opportunity types and locations they've applied to
before, plus a keyword search term if provided. This is intentionally
simple and dependency-free so it works before the `profiles` app's
Skill model lands — once ApplicantProfile/Skill exist, swap the scoring
function's inputs for real skill-overlap without changing the view.
"""
from django.db.models import Count, Q

from applications.models import Application
from opportunities.models import Opportunity


def get_recommended_opportunities(user, limit=10):
    if not user.is_authenticated or not user.is_applicant:
        return Opportunity.objects.none()

    applied_ids = Application.objects.filter(applicant=user).values_list("opportunity_id", flat=True)

    # Learn simple preferences from the applicant's own application history.
    past_types = (
        Application.objects.filter(applicant=user)
        .values_list("opportunity__opportunity_type", flat=True)
        .distinct()
    )
    past_locations = (
        Application.objects.filter(applicant=user)
        .values_list("opportunity__location", flat=True)
        .distinct()
    )

    candidates = Opportunity.objects.filter(is_active=True).exclude(id__in=applied_ids)

    if past_types or past_locations:
        candidates = candidates.annotate(
            type_match=Count("id", filter=Q(opportunity_type__in=list(past_types))),
            location_match=Count("id", filter=Q(location__in=list(past_locations))),
        ).order_by("-type_match", "-location_match", "-created_at")
    else:
        # New applicant with no history yet: just show the newest postings.
        candidates = candidates.order_by("-created_at")

    return candidates[:limit]
