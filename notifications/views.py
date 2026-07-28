from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .models import Notification


@login_required
def notification_list(request):
    notifications = Notification.objects.filter(recipient=request.user)
    return render(request, "notifications/list.html", {"notifications": notifications})


@login_required
def mark_read(request, pk):
    notification = get_object_or_404(Notification, pk=pk, recipient=request.user)
    notification.is_read = True
    notification.save(update_fields=["is_read"])
    if notification.link:
        return redirect(notification.link)
    return redirect("notifications:list")


@login_required
def mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True)
    return redirect("notifications:list")
