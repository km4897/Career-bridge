from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render

from .forms import ApplicantProfileForm, EmployerProfileForm
from .models import ApplicantProfile, EmployerProfile


@login_required
def edit_applicant_profile(request):
    if not request.user.is_applicant:
        messages.error(request, "Only applicant accounts have this type of profile.")
        return redirect("core:landing")

    profile, _ = ApplicantProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ApplicantProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profiles:edit_applicant")
    else:
        form = ApplicantProfileForm(instance=profile)

    return render(request, "profiles/applicant_profile_form.html", {"form": form, "profile": profile})


@login_required
def edit_employer_profile(request):
    if not request.user.is_employer:
        messages.error(request, "Only employer accounts have this type of profile.")
        return redirect("core:landing")

    profile, _ = EmployerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = EmployerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Organisation profile updated successfully.")
            return redirect("profiles:edit_employer")
    else:
        form = EmployerProfileForm(instance=profile)

    return render(request, "profiles/employer_profile_form.html", {"form": form, "profile": profile})
