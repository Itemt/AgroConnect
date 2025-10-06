from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Notification
from django.shortcuts import render


@login_required
@require_GET
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:20]
    data = [
        {
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'category': n.category,
            'order_id': n.order_id,
            'payment_id': n.payment_id,
            'created_at': timezone.localtime(n.created_at).isoformat(),
            'is_read': n.is_read,
        }
        for n in notifications
    ]
    return JsonResponse({'success': True, 'notifications': data})


@login_required
@require_POST
def notifications_mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    return JsonResponse({'success': True})

@login_required
@require_POST
def notifications_mark_all_unread(request):
    Notification.objects.filter(recipient=request.user, is_read=True).update(is_read=False, read_at=None)
    return JsonResponse({'success': True})


@login_required
@require_POST
def notifications_mark_read(request):
    import json
    data = json.loads(request.body)
    notification_id = data.get('notification_id')
    if notification_id:
        Notification.objects.filter(id=notification_id, recipient=request.user).update(is_read=True)
    return JsonResponse({'success': True})

from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'index.html')

@login_required
def notifications_page(request):
    """Vista para mostrar todas las notificaciones del usuario"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Paginación
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_notifications = notifications.count()
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'total_notifications': total_notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'core/notifications.html', context)
