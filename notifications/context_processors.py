"""
Makes the unread notification count available in every template
(so the navbar badge works on any page) without every view needing
to pass it in manually.
"""


def unread_notifications(request):
    if request.user.is_authenticated:
        count = request.user.notifications.filter(is_read=False).count()
    else:
        count = 0
    return {"unread_notifications_count": count}
