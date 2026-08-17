from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from applications.models import Application

from .forms import MessageForm


@login_required
def inbox(request):
    """Unified list of every conversation the current user is part of,
    across all their applications, sorted by most recent activity."""
    if request.user.is_applicant:
        applications = Application.objects.filter(applicant=request.user)
    elif request.user.is_employer:
        applications = Application.objects.filter(opportunity__employer=request.user)
    else:
        applications = Application.objects.none()

    applications = applications.select_related("opportunity", "applicant", "opportunity__employer")

    conversations = []
    for app in applications:
        last_message = app.messages.order_by("-sent_at").first()
        other_party = app.opportunity.employer if request.user == app.applicant else app.applicant
        conversations.append({
            "application": app,
            "other_party": other_party,
            "last_message": last_message,
            "activity_at": last_message.sent_at if last_message else app.submitted_at,
        })

    conversations.sort(key=lambda c: c["activity_at"], reverse=True)

    return render(request, "messaging/inbox.html", {"conversations": conversations})


@login_required
def thread(request, application_id):
    application = get_object_or_404(Application, pk=application_id)

    # Only the applicant or the employer who owns the opportunity may view/send.
    allowed = request.user == application.applicant or request.user == application.opportunity.employer
    if not allowed:
        raise PermissionDenied("You do not have access to this conversation.")

    if request.method == "POST":
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.application = application
            message.sender = request.user
            message.save()
            return redirect("messaging:thread", application_id=application.id)
    else:
        form = MessageForm()

    return render(request, "messaging/thread.html", {
        "application": application,
        "thread_messages": application.messages.select_related("sender"),
        "form": form,
    })
