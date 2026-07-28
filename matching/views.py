from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_recommended_opportunities


@login_required
def recommended(request):
    opportunities = get_recommended_opportunities(request.user)
    return render(request, "matching/recommended.html", {"opportunities": opportunities})
