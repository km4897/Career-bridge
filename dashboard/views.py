from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from applications.models import Application
from matching.services import get_recommended_opportunities
from opportunities.models import Opportunity

User = get_user_model()


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
    })


@login_required
def employer_dashboard(request):
    postings = Opportunity.objects.filter(employer=request.user)
    total_applicants = Application.objects.filter(opportunity__employer=request.user).count()
    unread_notifications = request.user.notifications.filter(is_read=False).count()
    return render(request, "dashboard/employer_dashboard.html", {
        "postings": postings,
        "total_applicants": total_applicants,
        "unread_notifications": unread_notifications,
    })


@login_required
def admin_dashboard(request):
    stats = {
        "total_users": User.objects.count(),
        "total_applicants": User.objects.filter(role=User.Role.APPLICANT).count(),
        "total_employers": User.objects.filter(role=User.Role.EMPLOYER).count(),
        "total_opportunities": Opportunity.objects.count(),
        "active_opportunities": Opportunity.objects.filter(is_active=True).count(),
        "total_applications": Application.objects.count(),
        "placements": Application.objects.filter(status=Application.Status.ACCEPTED).count(),
    }
    return render(request, "dashboard/admin_dashboard.html", {"stats": stats})
