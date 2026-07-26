from django.contrib.auth.decorators import login_required
from django.http import HttpResponse


@login_required
def recommended(request):
    # Placeholder: the scoring engine (services.py) will be wired in
    # once the Opportunity and ApplicantProfile models exist.
    return HttpResponse("Recommended opportunities placeholder — matching engine to be implemented.")
