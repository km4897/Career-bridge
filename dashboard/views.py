from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


@login_required
def redirect_dashboard(request):
    """Send the logged-in user to the dashboard for their role."""
    role = request.user.role
    if role == request.user.Role.APPLICANT:
        return redirect("dashboard:applicant")
    if role == request.user.Role.EMPLOYER:
        return redirect("dashboard:employer")
    return redirect("dashboard:admin")


@login_required
def applicant_dashboard(request):
    return render(request, "dashboard/applicant_dashboard.html")


@login_required
def employer_dashboard(request):
    return render(request, "dashboard/employer_dashboard.html")


@login_required
def admin_dashboard(request):
    return render(request, "dashboard/admin_dashboard.html")
