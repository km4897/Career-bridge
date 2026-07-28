from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import OpportunityForm, OpportunitySearchForm
from .models import Opportunity


def _employer_required(user):
    return user.is_authenticated and user.is_employer


def opportunity_list(request):
    """Public search/browse page. Anyone can view; only active postings show."""
    qs = Opportunity.objects.filter(is_active=True)
    form = OpportunitySearchForm(request.GET or None)

    if form.is_valid():
        q = form.cleaned_data.get("q")
        opp_type = form.cleaned_data.get("opportunity_type")
        location = form.cleaned_data.get("location")
        if q:
            qs = qs.filter(title__icontains=q) | qs.filter(description__icontains=q) | qs.filter(skills_required__icontains=q)
        if opp_type:
            qs = qs.filter(opportunity_type=opp_type)
        if location:
            qs = qs.filter(location__icontains=location)

    paginator = Paginator(qs.distinct(), 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "opportunities/list.html", {"form": form, "page_obj": page_obj})


def opportunity_detail(request, slug):
    opportunity = get_object_or_404(Opportunity, slug=slug)
    already_applied = False
    if request.user.is_authenticated and request.user.is_applicant:
        already_applied = opportunity.applications.filter(applicant=request.user).exists()
    return render(request, "opportunities/detail.html", {
        "opportunity": opportunity,
        "already_applied": already_applied,
    })


@login_required
def my_opportunities(request):
    """Employer's own postings, with quick management links."""
    if not _employer_required(request.user):
        messages.error(request, "Only employer accounts can manage opportunities.")
        return redirect("core:landing")
    postings = Opportunity.objects.filter(employer=request.user)
    return render(request, "opportunities/my_opportunities.html", {"postings": postings})


@login_required
def opportunity_create(request):
    if not _employer_required(request.user):
        messages.error(request, "Only employer accounts can post opportunities.")
        return redirect("core:landing")

    if request.method == "POST":
        form = OpportunityForm(request.POST)
        if form.is_valid():
            opportunity = form.save(commit=False)
            opportunity.employer = request.user
            opportunity.save()
            messages.success(request, "Opportunity posted successfully.")
            return redirect("opportunities:my_opportunities")
    else:
        form = OpportunityForm()
    return render(request, "opportunities/form.html", {"form": form, "mode": "Create"})


@login_required
def opportunity_update(request, slug):
    opportunity = get_object_or_404(Opportunity, slug=slug, employer=request.user)
    if request.method == "POST":
        form = OpportunityForm(request.POST, instance=opportunity)
        if form.is_valid():
            form.save()
            messages.success(request, "Opportunity updated.")
            return redirect("opportunities:my_opportunities")
    else:
        form = OpportunityForm(instance=opportunity)
    return render(request, "opportunities/form.html", {"form": form, "mode": "Edit"})


@login_required
def opportunity_delete(request, slug):
    opportunity = get_object_or_404(Opportunity, slug=slug, employer=request.user)
    if request.method == "POST":
        opportunity.delete()
        messages.success(request, "Opportunity deleted.")
        return redirect("opportunities:my_opportunities")
    return render(request, "opportunities/confirm_delete.html", {"opportunity": opportunity})
