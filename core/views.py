from django.shortcuts import render

from opportunities.models import Opportunity
from accounts.models import User


def landing(request):
    context = {
        "active_opportunities_count": Opportunity.objects.filter(is_active=True).count(),
        "employers_count": User.objects.filter(role=User.Role.EMPLOYER).count(),
        "applicants_count": User.objects.filter(role=User.Role.APPLICANT).count(),
    }
    return render(request, "core/landing.html", context)


def about(request):
    return render(request, "core/about.html")
