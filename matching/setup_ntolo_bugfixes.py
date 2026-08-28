"""
setup_ntolo_bugfixes.py -- Two real bugs found during QA, combined
into one script since both are yours to push

BUG 1 -- "Apply Now" skipped the application form
--------------------------------------------------
The opportunity detail page's "Apply Now" button was a self-submitting
<form method="post"> left over from before the per-vacancy application
form (name/phone/CV/cover note) was built. Clicking it POSTed directly
with an EMPTY body -- and since every field is optional, Django
silently created a blank Application (no CV, no cover note) and
redirected straight to My Applications. The real form was never shown.
Fix: "Apply Now" is now a plain link (GET) to the actual apply page.

BUG 2 -- Dashboard shows a real count, but the Recommended page shows
nothing
-----------------------------------------------------------------------
matching/views.py passes a context variable called "results", but the
template had drifted to an older version looping over a different
variable name ("opportunities"). Django never errors on an undefined
template variable -- a {% for %} over it just silently renders empty.
So the dashboard's stat card (which calls the underlying function
directly) showed a correct non-zero count, while the actual page
rendered its empty state regardless of real data existing. Fix: view,
service, and template are now packaged and written TOGETHER so they
can't drift apart again. Also restored the sidebar on this page, which
the stale template had also lost.

Both bugs were reproduced first (confirmed the exact symptom against a
clean clone), then fixed, then re-verified fixed, before this script
was built.

Run this from the ROOT of your cloned careerbridge repo, on a fresh
branch off main:

    git checkout main
    git pull origin main
    git checkout -b feature/ntolo-bugfixes
    python setup_ntolo_bugfixes.py
    python manage.py runserver

Then test:
    1. As an applicant, open any opportunity and click Apply Now --
       you should land on the real application form, not get silently
       redirected to My Applications with a blank entry.
    2. As an applicant with skills that overlap an open posting,
       compare the dashboard's "Recommended For You" count against the
       actual /matching/ page (via the stat card or the sidebar link)
       -- they should now show the same opportunities, with the
       sidebar visible on that page too.

This script only WRITES the files listed below.
"""
import os

BASE = os.path.dirname(os.path.abspath(__file__))

FILES = {
    'opportunities/templates/opportunities/detail.html': '{% extends "base.html" %}\n{% block title %}{{ opportunity.title }} — CareerBridge{% endblock %}\n{% block content %}\n<div class="d-flex justify-content-between align-items-start">\n  <h1>{{ opportunity.title }}</h1>\n  <span class="badge text-bg-primary fs-6">{{ opportunity.get_opportunity_type_display }}</span>\n</div>\n<p class="text-muted">{{ opportunity.location }} · {{ opportunity.duration_weeks }} weeks · Posted by {{ opportunity.employer.username }}</p>\n<p class="{% if opportunity.days_remaining <= 3 %}text-danger fw-bold{% else %}text-muted{% endif %}">\n  {% if opportunity.is_expired %}This opportunity has expired.{% else %}{{ opportunity.days_remaining }} day(s) remaining to apply{% endif %}\n</p>\n\n<hr>\n<p>{{ opportunity.description|linebreaks }}</p>\n\n{% if opportunity.skills_required %}\n  <p><strong>Skills required:</strong> {{ opportunity.skills_required }}</p>\n{% endif %}\n\n{% if user.is_authenticated and user.is_applicant %}\n  {% if already_applied %}\n    <p class="alert alert-info">You\'ve already applied to this opportunity.</p>\n  {% else %}\n    <a href="{% url \'applications:apply\' opportunity.slug %}" class="btn btn-success">Apply Now</a>\n  {% endif %}\n{% elif not user.is_authenticated %}\n  <a href="{% url \'accounts:login\' %}?next={{ request.path }}" class="btn btn-success">Log in to Apply</a>\n{% endif %}\n\n{% if user == opportunity.employer %}\n  <a href="{% url \'opportunities:update\' opportunity.slug %}" class="btn btn-outline-secondary mt-2">Edit Posting</a>\n  <a href="{% url \'applications:opportunity_applicants\' opportunity.slug %}" class="btn btn-outline-secondary mt-2">View Applicants</a>\n{% endif %}\n{% endblock %}\n',
    'matching/services.py': '"""\nRule-based recommendation engine (v2 — skill-based).\n\nScores active, non-expired opportunities for a given applicant primarily\nby skill overlap between the applicant\'s ApplicantProfile.skills and the\nopportunity\'s skills_required. Falls back to the v1 history-based\nscoring (past application types/locations) if the applicant hasn\'t\nlisted any skills yet, so the page is never empty for a new user.\n"""\nfrom django.db.models import Count, Q\n\nfrom applications.models import Application\nfrom opportunities.models import Opportunity\nfrom profiles.models import ApplicantProfile\n\n\ndef _skill_overlap_score(opportunity, applicant_skill_names):\n    """Number of the opportunity\'s required skills that the applicant has,\n    matched case-insensitively."""\n    opp_skills = {s.strip().lower() for s in opportunity.skills_list()}\n    return len(opp_skills & applicant_skill_names)\n\n\ndef get_matched_skills(opportunity, user):\n    """Which of the opportunity\'s required skills the applicant actually\n    has, for display purposes (e.g. \'Matched on: Python, Django\')."""\n    applicant_profile = ApplicantProfile.objects.filter(user=user).first()\n    if not applicant_profile:\n        return []\n    applicant_skill_names = {s.name.strip().lower() for s in applicant_profile.skills.all()}\n    opp_skills = opportunity.skills_list()\n    return [s for s in opp_skills if s.strip().lower() in applicant_skill_names]\n\n\ndef get_recommended_opportunities(user, limit=10):\n    if not user.is_authenticated or not user.is_applicant:\n        return Opportunity.objects.none()\n\n    applied_ids = Application.objects.filter(applicant=user).values_list("opportunity_id", flat=True)\n\n    candidate_ids = [\n        opp.id\n        for opp in Opportunity.objects.filter(is_active=True).exclude(id__in=applied_ids)\n        if not opp.is_expired\n    ]\n    candidates = list(Opportunity.objects.filter(id__in=candidate_ids))\n\n    applicant_profile = ApplicantProfile.objects.filter(user=user).first()\n    applicant_skill_names = set()\n    if applicant_profile:\n        applicant_skill_names = {s.name.strip().lower() for s in applicant_profile.skills.all()}\n\n    if applicant_skill_names:\n        # Primary path: real skill-overlap scoring.\n        scored = [\n            (opp, _skill_overlap_score(opp, applicant_skill_names))\n            for opp in candidates\n        ]\n        # Only treat it as a genuine skill match if at least one opportunity\n        # actually overlaps; otherwise fall through to the history-based\n        # scoring below so an applicant with niche skills still sees results.\n        if any(score > 0 for _, score in scored):\n            scored.sort(key=lambda pair: (pair[1], pair[0].created_at), reverse=True)\n            return [opp for opp, _ in scored][:limit]\n\n    # Fallback: learn simple preferences from application history\n    # (used for applicants with no skills listed yet, or no skill overlap).\n    past_types = (\n        Application.objects.filter(applicant=user)\n        .values_list("opportunity__opportunity_type", flat=True)\n        .distinct()\n    )\n    past_locations = (\n        Application.objects.filter(applicant=user)\n        .values_list("opportunity__location", flat=True)\n        .distinct()\n    )\n\n    fallback_qs = Opportunity.objects.filter(id__in=[c.id for c in candidates])\n\n    if past_types or past_locations:\n        fallback_qs = fallback_qs.annotate(\n            type_match=Count("id", filter=Q(opportunity_type__in=list(past_types))),\n            location_match=Count("id", filter=Q(location__in=list(past_locations))),\n        ).order_by("-type_match", "-location_match", "-created_at")\n    else:\n        fallback_qs = fallback_qs.order_by("-created_at")\n\n    return fallback_qs[:limit]\n',
    'matching/views.py': 'from django.contrib.auth.decorators import login_required\nfrom django.shortcuts import render\n\nfrom .services import get_matched_skills, get_recommended_opportunities\n\n\n@login_required\ndef recommended(request):\n    opportunities = get_recommended_opportunities(request.user)\n    results = [\n        {"opportunity": opp, "matched_skills": get_matched_skills(opp, request.user)}\n        for opp in opportunities\n    ]\n    return render(request, "matching/recommended.html", {"results": results})\n',
    'matching/templates/matching/recommended.html': '{% extends "app_base.html" %}\n{% load icons %}\n{% block title %}Recommended For You — CareerBridge{% endblock %}\n{% block app_content %}\n<h1 class="mb-4">Recommended For You</h1>\n{% if results %}\n  <div class="list-group">\n    {% for item in results %}\n      <a href="{{ item.opportunity.get_absolute_url }}" class="list-group-item list-group-item-action">\n        <h5 class="mb-1">{{ item.opportunity.title }}</h5>\n        <p class="mb-1 text-slate">{{ item.opportunity.location }} · {{ item.opportunity.get_opportunity_type_display }} · {{ item.opportunity.duration_weeks }} weeks</p>\n        {% if item.matched_skills %}\n          <small class="text-muted">Matched on: {{ item.matched_skills|join:", " }}</small>\n        {% endif %}\n      </a>\n    {% endfor %}\n  </div>\n{% else %}\n  <p class="text-slate">No recommendations yet — add some skills to your profile or apply to a few opportunities to get personalised suggestions.</p>\n{% endif %}\n{% endblock %}\n',
}

def main():
    for rel_path, content in FILES.items():
        full_path = os.path.join(BASE, rel_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"wrote {rel_path}")

    print()
    print("Done. Next steps:")
    print("  python manage.py runserver")
    print("  (test both fixes as described above)")

if __name__ == "__main__":
    main()
