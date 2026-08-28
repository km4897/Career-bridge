from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from .services import get_matched_skills, get_recommended_opportunities


@login_required
def recommended(request):
    opportunities = get_recommended_opportunities(request.user)
    results = [
        {"opportunity": opp, "matched_skills": get_matched_skills(opp, request.user)}
        for opp in opportunities
    ]
    return render(request, "matching/recommended.html", {"results": results})
