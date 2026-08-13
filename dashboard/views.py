from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from applications.models import Application
from matching.services import get_recommended_opportunities
from opportunities.models import Opportunity

User = get_user_model()


def _status_breakdown(queryset):
    """Returns an ordered list of {label, code, count, pct} for a
    status bar chart, based on Application.Status choices."""
    total = queryset.count()
    breakdown = []
    for code, label in Application.Status.choices:
        count = queryset.filter(status=code).count()
        pct = round((count / total) * 100) if total else 0
        breakdown.append({"label": label, "code": code, "count": count, "pct": pct})
    return breakdown


@login_required
def redirect_dashboard(request):
    role = request.user.role
    if role == request.user.Role.APPLICANT:
        return redirect("dashboard:applicant")
    if role == request.user.Role.EMPLOYER:
        return redirect("dashboard:employer")
    return redirect("dashboard:admin")


@login_required
def applicant_dashboard(request):
    applications = Application.objects.filter(applicant=request.user).select_related("opportunity")
    recommended = get_recommended_opportunities(request.user, limit=5)
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    return render(request, "dashboard/applicant_dashboard.html", {
        "applications": applications,
        "recommended": recommended,
        "unread_notifications": unread_notifications,
        "status_breakdown": _status_breakdown(applications),
    })


@login_required
def employer_dashboard(request):
    postings = Opportunity.objects.filter(employer=request.user)
    applicants = Application.objects.filter(opportunity__employer=request.user)
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    active_postings = postings.filter(is_active=True).count()
    return render(request, "dashboard/employer_dashboard.html", {
        "postings": postings,
        "total_applicants": applicants.count(),
        "active_postings": active_postings,
        "unread_notifications": unread_notifications,
        "status_breakdown": _status_breakdown(applicants),
        "recent_applicants": applicants.select_related("applicant", "opportunity").order_by("-submitted_at")[:5],
    })


@login_required
def admin_dashboard(request):
    all_applications = Application.objects.all()
    stats = {
        "total_users": User.objects.count(),
        "total_applicants": User.objects.filter(role=User.Role.APPLICANT).count(),
        "total_employers": User.objects.filter(role=User.Role.EMPLOYER).count(),
        "total_opportunities": Opportunity.objects.count(),
        "active_opportunities": Opportunity.objects.filter(is_active=True).count(),
        "total_applications": all_applications.count(),
        "placements": all_applications.filter(status=Application.Status.ACCEPTED).count(),
    }
    return render(request, "dashboard/admin_dashboard.html", {
        "stats": stats,
        "status_breakdown": _status_breakdown(all_applications),
    })
