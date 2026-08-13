from django.shortcuts import render

from opportunities.models import Opportunity
from accounts.models import User


def landing(request):
    featured = [
        opp for opp in Opportunity.objects.filter(is_active=True).order_by("-created_at")[:9]
        if not opp.is_expired
    ][:3]
    context = {
        "active_opportunities_count": Opportunity.objects.filter(is_active=True).count(),
        "employers_count": User.objects.filter(role=User.Role.EMPLOYER).count(),
        "applicants_count": User.objects.filter(role=User.Role.APPLICANT).count(),
        "featured_opportunities": featured,
    }
    return render(request, "core/landing.html", context)


def about(request):
    return render(request, "core/about.html")
