from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from applications.models import Application

from .forms import MessageForm


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
