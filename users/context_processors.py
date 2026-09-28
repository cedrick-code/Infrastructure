def notifications(request):
    if request.user.is_authenticated:
        from reports.models import Notification
        return {
            "unread_notifications_count": Notification.objects.filter(
                recipient=request.user, is_read=False
            ).count()
        }
    return {}