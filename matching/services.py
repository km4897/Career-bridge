"""
Rule-based recommendation engine (v2 — skill-based).

Scores active, non-expired opportunities for a given applicant primarily
by skill overlap between the applicant's ApplicantProfile.skills and the
opportunity's skills_required. Falls back to the v1 history-based
scoring (past application types/locations) if the applicant hasn't
listed any skills yet, so the page is never empty for a new user.
"""
from django.db.models import Count, Q

from applications.models import Application
from opportunities.models import Opportunity
from profiles.models import ApplicantProfile


def _skill_overlap_score(opportunity, applicant_skill_names):
    """Number of the opportunity's required skills that the applicant has,
    matched case-insensitively."""
    opp_skills = {s.strip().lower() for s in opportunity.skills_list()}
    return len(opp_skills & applicant_skill_names)


def get_matched_skills(opportunity, user):
    """Which of the opportunity's required skills the applicant actually
    has, for display purposes (e.g. 'Matched on: Python, Django')."""
    applicant_profile = ApplicantProfile.objects.filter(user=user).first()
    if not applicant_profile:
        return []
    applicant_skill_names = {s.name.strip().lower() for s in applicant_profile.skills.all()}
    opp_skills = opportunity.skills_list()
    return [s for s in opp_skills if s.strip().lower() in applicant_skill_names]


def get_recommended_opportunities(user, limit=10):
    if not user.is_authenticated or not user.is_applicant:
        return Opportunity.objects.none()

    applied_ids = Application.objects.filter(applicant=user).values_list("opportunity_id", flat=True)

    candidate_ids = [
        opp.id
        for opp in Opportunity.objects.filter(is_active=True).exclude(id__in=applied_ids)
        if not opp.is_expired
    ]
    candidates = list(Opportunity.objects.filter(id__in=candidate_ids))

    applicant_profile = ApplicantProfile.objects.filter(user=user).first()
    applicant_skill_names = set()
    if applicant_profile:
        applicant_skill_names = {s.name.strip().lower() for s in applicant_profile.skills.all()}

    if applicant_skill_names:
        # Primary path: real skill-overlap scoring.
        scored = [
            (opp, _skill_overlap_score(opp, applicant_skill_names))
            for opp in candidates
        ]
        # Only treat it as a genuine skill match if at least one opportunity
        # actually overlaps; otherwise fall through to the history-based
        # scoring below so an applicant with niche skills still sees results.
        if any(score > 0 for _, score in scored):
            scored.sort(key=lambda pair: (pair[1], pair[0].created_at), reverse=True)
            return [opp for opp, _ in scored][:limit]

    # Fallback: learn simple preferences from application history
    # (used for applicants with no skills listed yet, or no skill overlap).
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

    fallback_qs = Opportunity.objects.filter(id__in=[c.id for c in candidates])

    if past_types or past_locations:
        fallback_qs = fallback_qs.annotate(
            type_match=Count("id", filter=Q(opportunity_type__in=list(past_types))),
            location_match=Count("id", filter=Q(location__in=list(past_locations))),
        ).order_by("-type_match", "-location_match", "-created_at")
    else:
        fallback_qs = fallback_qs.order_by("-created_at")

    return fallback_qs[:limit]
