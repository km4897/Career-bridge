from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from opportunities.models import Opportunity

from .forms import ApplicationForm, ApplicationStatusForm
from .models import Application


@login_required
def apply_to_opportunity(request, slug):
    opportunity = get_object_or_404(Opportunity, slug=slug, is_active=True)

    if opportunity.is_expired:
        messages.error(request, "This opportunity has expired and is no longer accepting applications.")
        return redirect("opportunities:list")

    if not request.user.is_applicant:
        messages.error(request, "Only applicant accounts can apply to opportunities.")
        return redirect(opportunity.get_absolute_url())

    if Application.objects.filter(applicant=request.user, opportunity=opportunity).exists():
        messages.info(request, "You've already applied to this opportunity.")
        return redirect(opportunity.get_absolute_url())

    if request.method == "POST":
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.applicant = request.user
            application.opportunity = opportunity
            application.save()
            messages.success(request, "Application submitted successfully.")
            return redirect("applications:my_applications")
    else:
        profile = getattr(request.user, "applicant_profile", None)
        initial = {}
        if profile:
            initial["full_name"] = profile.full_name
        form = ApplicationForm(initial=initial)

    return render(request, "applications/apply_form.html", {
        "form": form, "opportunity": opportunity,
        "profile": getattr(request.user, "applicant_profile", None),
    })


@login_required
def my_applications(request):
    if not request.user.is_applicant:
        messages.error(request, "Only applicant accounts have an applications list.")
        return redirect("core:landing")

    all_applications = Application.objects.filter(applicant=request.user).select_related("opportunity")

    status_filter = request.GET.get("status", "")
    if status_filter and status_filter in Application.Status.values:
        applications = all_applications.filter(status=status_filter)
    else:
        applications = all_applications
        status_filter = ""

    # Tab list: "All" plus one per status, each with a live count.
    tabs = [{"code": "", "label": "All", "count": all_applications.count()}]
    for code, label in Application.Status.choices:
        count = all_applications.filter(status=code).count()
        tabs.append({"code": code, "label": label, "count": count})

    return render(request, "applications/my_applications.html", {
        "applications": applications,
        "tabs": tabs,
        "active_status": status_filter,
    })


@login_required
def opportunity_applicants(request, slug):
    opportunity = get_object_or_404(Opportunity, slug=slug, employer=request.user)
    applications = opportunity.applications.select_related("applicant")
    return render(request, "applications/opportunity_applicants.html", {
        "opportunity": opportunity,
        "applications": applications,
        "status_form": ApplicationStatusForm(),
    })


@login_required
def update_application_status(request, pk):
    application = get_object_or_404(Application, pk=pk, opportunity__employer=request.user)
    if request.method == "POST":
        form = ApplicationStatusForm(request.POST, instance=application)
        if form.is_valid():
            application = form.save(commit=False)
            application.decision_at = timezone.now()
            application.save()
            messages.success(request, f"Status updated to {application.get_status_display()}.")
    return redirect("applications:opportunity_applicants", slug=application.opportunity.slug)
