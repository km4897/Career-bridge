from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def placeholder(request):
    return render(request, "profiles/placeholder.html", {"app_name": "profiles"})
