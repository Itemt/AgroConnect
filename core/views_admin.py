"""
Vistas para el panel de administración de la aplicación web
"""
from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum, Q
from datetime import datetime, timedelta
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
    
    # Estadísticas generales
    stats = {
        'total_users': User.objects.count(),
        'total_crops': Crop.objects.count(),
        'total_publications': Publication.objects.count(),
        'total_orders': Order.objects.count(),
        'completed_orders': Order.objects.filter(estado='Completado').count(),
        'pending_orders': Order.objects.filter(estado='Pendiente').count(),
        'total_sales': Order.objects.filter(estado='Completado').aggregate(
            total=Sum('total')
        )['total'] or 0,
    }
    
    # Usuarios por rol
    users_by_role = User.objects.values('role').annotate(count=Count('id'))
    
    # Usuarios recientes
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    # Pedidos recientes
    recent_orders = Order.objects.select_related('comprador', 'vendedor').order_by('-created_at')[:5]
    
    # Notificaciones recientes
    recent_notifications = Notification.objects.order_by('-created_at')[:5]
    
    # Cultivos por estado
    crops_by_status = Crop.objects.values('estado').annotate(count=Count('id'))
    
    # Estadísticas de ventas por mes (últimos 6 meses)
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_sales = Order.objects.filter(
        estado='Completado',
        created_at__gte=six_months_ago
    ).extra(
        select={'month': "EXTRACT(month FROM created_at)"}
    ).values('month').annotate(
        total_sales=Sum('total'),
        count=Count('id')
    ).order_by('month')
    
    context = {
        'stats': stats,
        'users_by_role': users_by_role,
        'recent_users': recent_users,
        'recent_orders': recent_orders,
        'recent_notifications': recent_notifications,
        'crops_by_status': crops_by_status,
        'monthly_sales': monthly_sales,
    }
    
    return render(request, 'core/admin_dashboard.html', context)

@user_passes_test(is_admin)
def admin_users(request):
    """Gestión de usuarios"""
    users = User.objects.all().order_by('-date_joined')
    
    # Filtros
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(role=role_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
    
    context = {
        'users': users,
        'role_choices': User.ROLE_CHOICES,
        'current_role': role_filter,
        'search_query': search_query,
    }
    
    return render(request, 'core/admin_users.html', context)

@user_passes_test(is_admin)
def admin_crops(request):
    """Gestión de cultivos"""
    crops = Crop.objects.select_related('productor').order_by('-created_at')
    
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
    
    context = {
        'crops': crops,
        'status_choices': [
            ('en_cultivo', 'En Cultivo'),
            ('listo_cosecha', 'Listo para Cosecha'),
            ('cosechado', 'Cosechado'),
            ('disponible', 'Disponible'),
        ],
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'core/admin_crops.html', context)

@user_passes_test(is_admin)
def admin_orders(request):
    """Gestión de pedidos"""
    orders = Order.objects.select_related('comprador', 'vendedor').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        orders = orders.filter(estado=status_filter)
    
    search_query = request.GET.get('search')
    if search_query:
        orders = orders.filter(
            Q(comprador__username__icontains=search_query) |
            Q(vendedor__username__icontains=search_query) |
            Q(id__icontains=search_query)
        )
    
    context = {
        'orders': orders,
        'status_choices': [
            ('Pendiente', 'Pendiente'),
            ('Confirmado', 'Confirmado'),
            ('En_Proceso', 'En Proceso'),
            ('Enviado', 'Enviado'),
            ('Completado', 'Completado'),
            ('Cancelado', 'Cancelado'),
        ],
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'core/admin_orders.html', context)

@user_passes_test(is_admin)
def admin_publications(request):
    """Gestión de publicaciones"""
    publications = Publication.objects.select_related('vendedor', 'crop').order_by('-created_at')
    
    # Filtros
    status_filter = request.GET.get('status')
    if status_filter:
        publications = publications.filter(activa=status_filter == 'activa')
    
    search_query = request.GET.get('search')
    if search_query:
        publications = publications.filter(
            Q(titulo__icontains=search_query) |
            Q(vendedor__username__icontains=search_query) |
            Q(crop__nombre__icontains=search_query)
        )
    
    context = {
        'publications': publications,
        'current_status': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'core/admin_publications.html', context)
