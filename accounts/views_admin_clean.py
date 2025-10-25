"""
Vistas de administración para la aplicación web
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q, Count
from django.core.paginator import Paginator
from inventory.models import Crop
from sales.models import Order
from marketplace.models import Publication
from core.models import Notification

User = get_user_model()

def is_admin(user):
    """Verifica si el usuario es administrador"""
    return user.is_authenticated and (user.is_superuser or user.role == 'Admin')

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Dashboard principal de administración"""
    from django.utils import timezone
    from datetime import timedelta, datetime
    from django.db.models import Sum, Avg, Q
    
    # Fechas para comparaciones
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    # Estadísticas principales
    stats = {
        'total_users': User.objects.count(),
        'total_crops': Crop.objects.count(),
        'total_publications': Publication.objects.count(),
        'total_orders': Order.objects.count(),
    }
    
    # Estadísticas de usuarios
    user_stats = {
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
        'admin_users': User.objects.filter(role='Admin').count(),
        'producer_users': User.objects.filter(role='Productor').count(),
        'buyer_users': User.objects.filter(role='Comprador').count(),
        'new_users_today': User.objects.filter(date_joined__date=today).count(),
        'new_users_week': User.objects.filter(date_joined__date__gte=last_week).count(),
        'new_users_month': User.objects.filter(date_joined__date__gte=last_month).count(),
    }
    
    # Estadísticas de cultivos
    crop_stats = {
        'total_crops': Crop.objects.count(),
        'crops_en_crecimiento': Crop.objects.filter(estado='en_crecimiento').count(),
        'crops_listo_para_cosechar': Crop.objects.filter(estado='listo_para_cosechar').count(),
        'crops_cosechado': Crop.objects.filter(estado='cosechado').count(),
        'crops_sembrado': Crop.objects.filter(estado='sembrado').count(),
        'crops_today': Crop.objects.filter(created_at__date=today).count(),
        'crops_week': Crop.objects.filter(created_at__date__gte=last_week).count(),
    }
    
    # Estadísticas de publicaciones
    publication_stats = {
        'total_publications': Publication.objects.count(),
        'active_publications': Publication.objects.filter(estado='Activa').count(),
        'paused_publications': Publication.objects.filter(estado='Pausada').count(),
        'sold_out_publications': Publication.objects.filter(estado='Agotada').count(),
        'publications_today': Publication.objects.filter(created_at__date=today).count(),
        'publications_week': Publication.objects.filter(created_at__date__gte=last_week).count(),
    }
    
    # Estadísticas de pedidos
    order_stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(estado='pendiente').count(),
        'confirmed_orders': Order.objects.filter(estado='confirmado').count(),
        'shipped_orders': Order.objects.filter(estado='enviado').count(),
        'completed_orders': Order.objects.filter(estado='completado').count(),
        'cancelled_orders': Order.objects.filter(estado='cancelado').count(),
        'orders_today': Order.objects.filter(created_at__date=today).count(),
        'orders_week': Order.objects.filter(created_at__date__gte=last_week).count(),
    }
    
    # Ingresos
    revenue_stats = {
        'total_revenue': Order.objects.filter(estado='completado').aggregate(
            total=Sum('precio_total')
        )['total'] or 0,
        'revenue_today': Order.objects.filter(
            estado='completado',
            created_at__date=today
        ).aggregate(total=Sum('precio_total'))['total'] or 0,
        'revenue_week': Order.objects.filter(
            estado='completado',
            created_at__date__gte=last_week
        ).aggregate(total=Sum('precio_total'))['total'] or 0,
        'revenue_month': Order.objects.filter(
            estado='completado',
            created_at__date__gte=last_month
        ).aggregate(total=Sum('precio_total'))['total'] or 0,
    }
    
    # Actividad reciente
    recent_activity = {
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_crops': Crop.objects.order_by('-created_at')[:5],
        'recent_publications': Publication.objects.order_by('-created_at')[:5],
        'recent_orders': Order.objects.order_by('-created_at')[:5],
    }
    
    context = {
        'stats': stats,
        'user_stats': user_stats,
        'crop_stats': crop_stats,
        'publication_stats': publication_stats,
        'order_stats': order_stats,
        'revenue_stats': revenue_stats,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'accounts/admin_dashboard_tailadmin.html', context)

@user_passes_test(is_admin)
def admin_user_list(request):
    """Lista de usuarios"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filtros
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'role_choices': User.ROLE_CHOICES,
        'current_role': role_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_user_list_tailadmin.html', context)

@user_passes_test(is_admin)
def admin_crop_list(request):
    """Lista de cultivos"""
    crops = Crop.objects.select_related('productor', 'finca').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        crops = crops.filter(estado=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        crops = crops.filter(
            Q(nombre__icontains=search_query) |
            Q(productor__username__icontains=search_query) |
            Q(categoria__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(crops, 20)
    page_number = request.GET.get('page')
    crops = paginator.get_page(page_number)
    
    context = {
        'crops': crops,
        'status_choices': [
            ('sembrado', 'Sembrado'),
            ('en_crecimiento', 'En Crecimiento'),
            ('listo_para_cosechar', 'Listo para Cosechar'),
            ('cosechado', 'Cosechado'),
        ],
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_crop_list_tailadmin.html', context)

@user_passes_test(is_admin)
def admin_order_list(request):
    """Lista de pedidos"""
    orders = Order.objects.select_related('comprador', 'publicacion', 'publicacion__cultivo', 'publicacion__cultivo__productor').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(estado=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(comprador__username__icontains=search_query) |
            Q(publicacion__cultivo__nombre__icontains=search_query) |
            Q(publicacion__cultivo__productor__username__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'orders': orders,
        'status_choices': [
            ('pendiente', 'Pendiente'),
            ('confirmado', 'Confirmado'),
            ('en_preparacion', 'En Preparación'),
            ('enviado', 'Enviado'),
            ('en_transito', 'En Tránsito'),
            ('recibido', 'Recibido'),
            ('completado', 'Completado'),
            ('cancelado', 'Cancelado'),
        ],
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_order_list_tailadmin.html', context)

@user_passes_test(is_admin)
def admin_publication_list(request):
    """Lista de publicaciones"""
    publications = Publication.objects.select_related('cultivo', 'finca').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        publications = publications.filter(estado=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        publications = publications.filter(
            Q(descripcion__icontains=search_query) |
            Q(cultivo__productor__username__icontains=search_query) |
            Q(cultivo__nombre__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(publications, 20)
    page_number = request.GET.get('page')
    publications = paginator.get_page(page_number)
    
    context = {
        'publications': publications,
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_publication_list_tailadmin.html', context)

# Funciones de preview (sin autenticación)
def admin_user_list_preview(request):
    """Vista de preview de usuarios sin autenticación"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filtros
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(users, 20)
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    
    context = {
        'users': users,
        'current_role': role_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_user_list_tailadmin.html', context)

def admin_order_list_preview(request):
    """Vista de preview de pedidos sin autenticación"""
    orders = Order.objects.select_related('comprador', 'publicacion', 'publicacion__cultivo', 'publicacion__cultivo__productor').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(estado=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(comprador__username__icontains=search_query) |
            Q(publicacion__cultivo__nombre__icontains=search_query) |
            Q(publicacion__cultivo__productor__username__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    orders = paginator.get_page(page_number)
    
    context = {
        'orders': orders,
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_order_list_tailadmin.html', context)

def admin_crop_list_preview(request):
    """Vista de preview de cultivos sin autenticación"""
    crops = Crop.objects.select_related('productor', 'finca').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        crops = crops.filter(estado=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        crops = crops.filter(
            Q(nombre__icontains=search_query) |
            Q(productor__username__icontains=search_query) |
            Q(categoria__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(crops, 20)
    page_number = request.GET.get('page')
    crops = paginator.get_page(page_number)
    
    context = {
        'crops': crops,
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_crop_list_tailadmin.html', context)

def admin_publication_list_preview(request):
    """Vista de preview de publicaciones sin autenticación"""
    publications = Publication.objects.select_related('cultivo', 'finca').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        publications = publications.filter(estado=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        publications = publications.filter(
            Q(descripcion__icontains=search_query) |
            Q(cultivo__productor__username__icontains=search_query) |
            Q(cultivo__nombre__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(publications, 20)
    page_number = request.GET.get('page')
    publications = paginator.get_page(page_number)
    
    context = {
        'publications': publications,
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_publication_list_tailadmin.html', context)

def admin_dashboard_preview(request):
    """Vista de preview del dashboard sin autenticación"""
    from django.utils import timezone
    from datetime import timedelta, datetime
    from django.db.models import Sum, Avg, Q
    
    # Fechas para comparaciones
    now = timezone.now()
    today = now.date()
    yesterday = today - timedelta(days=1)
    last_week = today - timedelta(days=7)
    last_month = today - timedelta(days=30)
    
    # Estadísticas principales
    stats = {
        'total_users': User.objects.count(),
        'total_crops': Crop.objects.count(),
        'total_publications': Publication.objects.count(),
        'total_orders': Order.objects.count(),
    }
    
    # Estadísticas de usuarios
    user_stats = {
        'active_users': User.objects.filter(is_active=True).count(),
        'inactive_users': User.objects.filter(is_active=False).count(),
        'admin_users': User.objects.filter(role='Admin').count(),
        'producer_users': User.objects.filter(role='Productor').count(),
        'buyer_users': User.objects.filter(role='Comprador').count(),
        'new_users_today': User.objects.filter(date_joined__date=today).count(),
        'new_users_week': User.objects.filter(date_joined__date__gte=last_week).count(),
        'new_users_month': User.objects.filter(date_joined__date__gte=last_month).count(),
    }
    
    # Estadísticas de cultivos
    crop_stats = {
        'total_crops': Crop.objects.count(),
        'crops_en_crecimiento': Crop.objects.filter(estado='en_crecimiento').count(),
        'crops_listo_para_cosechar': Crop.objects.filter(estado='listo_para_cosechar').count(),
        'crops_cosechado': Crop.objects.filter(estado='cosechado').count(),
        'crops_sembrado': Crop.objects.filter(estado='sembrado').count(),
        'crops_today': Crop.objects.filter(created_at__date=today).count(),
        'crops_week': Crop.objects.filter(created_at__date__gte=last_week).count(),
    }
    
    # Estadísticas de publicaciones
    publication_stats = {
        'total_publications': Publication.objects.count(),
        'active_publications': Publication.objects.filter(estado='Activa').count(),
        'paused_publications': Publication.objects.filter(estado='Pausada').count(),
        'sold_out_publications': Publication.objects.filter(estado='Agotada').count(),
        'publications_today': Publication.objects.filter(created_at__date=today).count(),
        'publications_week': Publication.objects.filter(created_at__date__gte=last_week).count(),
    }
    
    # Estadísticas de pedidos
    order_stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(estado='pendiente').count(),
        'confirmed_orders': Order.objects.filter(estado='confirmado').count(),
        'shipped_orders': Order.objects.filter(estado='enviado').count(),
        'completed_orders': Order.objects.filter(estado='completado').count(),
        'cancelled_orders': Order.objects.filter(estado='cancelado').count(),
        'orders_today': Order.objects.filter(created_at__date=today).count(),
        'orders_week': Order.objects.filter(created_at__date__gte=last_week).count(),
    }
    
    # Ingresos
    revenue_stats = {
        'total_revenue': Order.objects.filter(estado='completado').aggregate(
            total=Sum('precio_total')
        )['total'] or 0,
        'revenue_today': Order.objects.filter(
            estado='completado',
            created_at__date=today
        ).aggregate(total=Sum('precio_total'))['total'] or 0,
        'revenue_week': Order.objects.filter(
            estado='completado',
            created_at__date__gte=last_week
        ).aggregate(total=Sum('precio_total'))['total'] or 0,
        'revenue_month': Order.objects.filter(
            estado='completado',
            created_at__date__gte=last_month
        ).aggregate(total=Sum('precio_total'))['total'] or 0,
    }
    
    # Actividad reciente
    recent_activity = {
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_crops': Crop.objects.order_by('-created_at')[:5],
        'recent_publications': Publication.objects.order_by('-created_at')[:5],
        'recent_orders': Order.objects.order_by('-created_at')[:5],
    }
    
    context = {
        'stats': stats,
        'user_stats': user_stats,
        'crop_stats': crop_stats,
        'publication_stats': publication_stats,
        'order_stats': order_stats,
        'revenue_stats': revenue_stats,
        'recent_activity': recent_activity,
    }
    
    return render(request, 'accounts/admin_dashboard_tailadmin.html', context)

# Funciones auxiliares para compatibilidad

def admin_dashboard_simple(request):
    """Dashboard simple"""
    return render(request, 'accounts/admin_dashboard_simple.html', {})

def admin_dashboard_inline(request):
    """Dashboard inline"""
    return render(request, 'accounts/admin_dashboard_inline.html', {})

def admin_debug(request):
    """Vista de debug"""
    return render(request, 'accounts/admin_debug.html', {})
