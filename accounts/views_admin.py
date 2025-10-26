"""
Vistas de administración para la aplicación web
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.db.models import Q, Count, Sum, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from django.db.models.functions import TruncMonth
import json
from inventory.models import Crop
from inventory.forms import AdminCropForm
from marketplace.models import Publication
from marketplace.forms import AdminPublicationForm
from sales.models import Order
from sales.models import Conversation, Message
from accounts.models import AdminAction
from core.models import Notification, Farm
from core.forms import AdminFarmForm

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
    
    # Datos para gráficas
    from django.db.models.functions import Extract
    
    # Crecimiento mensual de usuarios (últimos 6 meses)
    monthly_growth = []
    for i in range(6):
        month_date = now - timedelta(days=30*i)
        month_start = month_date.replace(day=1)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
        
        users_count = User.objects.filter(
            date_joined__date__gte=month_start,
            date_joined__date__lte=month_end
        ).count()
        
        monthly_growth.append({
            'month': month_start.strftime('%b %Y'),
            'users': users_count
        })
    
    monthly_growth.reverse()  # Ordenar cronológicamente
    
    # Distribución de estados de pedidos
    order_status_distribution = Order.objects.values('estado').annotate(
        count=Count('id')
    ).order_by('estado')
    
    # Actividad reciente
    recent_activity = {
        'recent_users': User.objects.order_by('-date_joined')[:5],
        'recent_crops': Crop.objects.order_by('-created_at')[:5],
        'recent_publications': Publication.objects.order_by('-created_at')[:5],
        'recent_orders': Order.objects.order_by('-created_at')[:5],
    }
    
    # Estadísticas financieras
    financial_stats = {
        'total_revenue': revenue_stats['total_revenue'],
        'pending_revenue': Order.objects.filter(estado__in=['pendiente', 'confirmado']).aggregate(
            total=Sum('precio_total')
        )['total'] or 0,
        'avg_order_value': Order.objects.filter(estado='completado').aggregate(
            avg=Avg('precio_total')
        )['avg'] or 0,
    }
    
    context = {
        'stats': stats,
        'user_stats': user_stats,
        'crop_stats': crop_stats,
        'publication_stats': publication_stats,
        'order_stats': order_stats,
        'revenue_stats': revenue_stats,
        'financial_stats': financial_stats,
        'monthly_growth': json.dumps(monthly_growth),
        'order_status_distribution': json.dumps(list(order_status_distribution)),
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
    from django.db.models import Sum, Avg, Q, Count
    from django.db.models.functions import Extract
    
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
    
    # Datos para gráficos - Crecimiento de usuarios (últimos 6 meses)
    six_months_ago = now - timedelta(days=180)
    monthly_users = User.objects.filter(date_joined__gte=six_months_ago).annotate(
        month=Extract('date_joined', 'month')
    ).values('month').annotate(count=Count('id')).order_by('month')
    
    monthly_growth = []
    months = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun']
    month_numbers = [1, 2, 3, 4, 5, 6]
    
    for i, month in enumerate(months):
        month_num = month_numbers[i]
        count = next((item['count'] for item in monthly_users if item['month'] == month_num), 0)
        monthly_growth.append({'month': month, 'users': count})
    
    # Distribución de estados de pedidos
    order_status_distribution = []
    for status, _ in Order.ESTADO_CHOICES:
        count = Order.objects.filter(estado=status).count()
        if count > 0:
            order_status_distribution.append({'estado': status, 'count': count})
    
    context = {
        'stats': stats,
        'user_stats': user_stats,
        'crop_stats': crop_stats,
        'publication_stats': publication_stats,
        'order_stats': order_stats,
        'revenue_stats': revenue_stats,
        'recent_activity': recent_activity,
        'monthly_growth': monthly_growth,
        'order_status_distribution': order_status_distribution,
    }
    
    return render(request, 'accounts/admin_dashboard_tailadmin.html', context)

# Funciones auxiliares para compatibilidad

# Funciones CRUD para usuarios
@user_passes_test(is_admin)
def admin_user_create(request):
    """Crear usuario"""
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'  # Checkbox marcado
        password = request.POST.get('password1')
        password2 = request.POST.get('password2')
        
        # Campos adicionales del modelo User
        cedula = request.POST.get('cedula', '')
        telefono = request.POST.get('telefono', '')
        departamento = request.POST.get('departamento', '')
        ciudad = request.POST.get('ciudad', '')
        
        # Campos de la finca (solo si es Productor)
        finca_nombre = request.POST.get('finca_nombre', '')
        finca_area = request.POST.get('finca_area', '')
        finca_departamento = request.POST.get('finca_departamento', '')
        finca_ciudad = request.POST.get('finca_ciudad', '')
        finca_direccion = request.POST.get('finca_direccion', '')
        finca_descripcion = request.POST.get('finca_descripcion', '')
        finca_cultivos = request.POST.get('finca_cultivos', '')
        
        
        # Validaciones básicas
        if not username or not email or not role or not password:
            messages.error(request, 'Todos los campos obligatorios deben ser completados.')
            return render(request, 'accounts/admin_user_form.html', {
                'role_choices': User.ROLE_CHOICES,
                'is_create': True,
                'title': 'Crear Nuevo Usuario',
            })
        
        # Validaciones específicas para Productores
        if role == 'Productor':
            if not finca_nombre or not finca_departamento or not finca_ciudad:
                messages.error(request, 'Los productores deben tener información completa de la finca.')
                return render(request, 'accounts/admin_user_form.html', {
                    'role_choices': User.ROLE_CHOICES,
                    'is_create': True,
                    'title': 'Crear Nuevo Usuario',
                })
        
        # Validar que las contraseñas coincidan
        if password != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'accounts/admin_user_form.html', {
                'role_choices': User.ROLE_CHOICES,
                'is_create': True,
                'title': 'Crear Nuevo Usuario',
            })
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'accounts/admin_user_form.html', {
                'role_choices': User.ROLE_CHOICES,
                'is_create': True,
                'title': 'Crear Nuevo Usuario',
            })
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'El email ya está registrado.')
            return render(request, 'accounts/admin_user_form.html', {
                'role_choices': User.ROLE_CHOICES,
                'is_create': True,
                'title': 'Crear Nuevo Usuario',
            })
        
        try:
            # Crear el usuario
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role=role,
                is_active=is_active,
                has_password=True,
                is_google_user=False,
                cedula=cedula if cedula else None,
                telefono=telefono if telefono else None,
                departamento=departamento if departamento else None,
                ciudad=ciudad if ciudad else None,
                can_sell=(role == 'Productor')  # Solo los productores pueden vender por defecto
            )
            
            # Si es Productor, crear la finca
            if role == 'Productor':
                from core.models import Farm
                farm = Farm.objects.create(
                    user=user,
                    nombre=finca_nombre,
                    departamento=finca_departamento,
                    ciudad=finca_ciudad,
                    direccion=finca_direccion if finca_direccion else None,
                    descripcion=finca_descripcion if finca_descripcion else None,
                    area=float(finca_area) if finca_area else None,
                    cultivos_principales=finca_cultivos if finca_cultivos else None,
                    activa=True
                )
            
            # Registrar la acción de creación
            from .admin_audit import log_user_action
            log_user_action(
                admin_user=request.user,
                action_type='create',
                user=user,
                request=request,
                changes={
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                    'is_active': user.is_active,
                    'cedula': cedula,
                    'telefono': telefono,
                    'departamento': departamento,
                    'ciudad': ciudad,
                    'finca_creada': role == 'Productor'
                }
            )
            
            messages.success(request, f'Usuario "{user.username}" creado exitosamente.')
            return redirect('admin_user_list')
        except Exception as e:
            messages.error(request, f'Error al crear el usuario: {str(e)}')
    
    context = {
        'role_choices': User.ROLE_CHOICES,
        'is_create': True,
        'title': 'Crear Nuevo Usuario',
    }
    return render(request, 'accounts/admin_user_form.html', context)

@user_passes_test(is_admin)
def admin_user_edit(request, pk):
    """Editar usuario"""
    user = get_object_or_404(User, pk=pk)
    
    if request.method == 'POST':
        # Obtener datos del formulario
        username = request.POST.get('username')
        email = request.POST.get('email')
        first_name = request.POST.get('first_name', '')
        last_name = request.POST.get('last_name', '')
        role = request.POST.get('role')
        is_active = request.POST.get('is_active') == 'on'
        
        # Campos adicionales del modelo User
        cedula = request.POST.get('cedula', '')
        telefono = request.POST.get('telefono', '')
        departamento = request.POST.get('departamento', '')
        ciudad = request.POST.get('ciudad', '')
        
        # Campos de la finca (solo si es Productor)
        finca_nombre = request.POST.get('finca_nombre', '')
        finca_area = request.POST.get('finca_area', '')
        finca_departamento = request.POST.get('finca_departamento', '')
        finca_ciudad = request.POST.get('finca_ciudad', '')
        finca_direccion = request.POST.get('finca_direccion', '')
        finca_descripcion = request.POST.get('finca_descripcion', '')
        finca_cultivos = request.POST.get('finca_cultivos', '')
        
        # Validaciones básicas
        if not username or not email or not role:
            messages.error(request, 'Todos los campos obligatorios deben ser completados.')
            return render(request, 'accounts/admin_user_form.html', {
                'user': user,
                'role_choices': User.ROLE_CHOICES,
                'is_create': False,
                'title': f'Editar Usuario: {user.username}',
            })
        
        # Validaciones específicas para Productores
        if role == 'Productor':
            if not finca_nombre or not finca_departamento or not finca_ciudad:
                messages.error(request, 'Los productores deben tener información completa de la finca.')
                return render(request, 'accounts/admin_user_form.html', {
                    'user': user,
                    'role_choices': User.ROLE_CHOICES,
                    'is_create': False,
                    'title': f'Editar Usuario: {user.username}',
                })
        
        # Verificar si el username ya existe (excluyendo el usuario actual)
        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, 'El nombre de usuario ya existe.')
            return render(request, 'accounts/admin_user_form.html', {
                'user': user,
                'role_choices': User.ROLE_CHOICES,
                'is_create': False,
                'title': f'Editar Usuario: {user.username}',
            })
        
        # Verificar si el email ya existe (excluyendo el usuario actual)
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            messages.error(request, 'El email ya está registrado.')
            return render(request, 'accounts/admin_user_form.html', {
                'user': user,
                'role_choices': User.ROLE_CHOICES,
                'is_create': False,
                'title': f'Editar Usuario: {user.username}',
            })
        
        try:
            # Actualizar el usuario
            user.username = username
            user.email = email
            user.first_name = first_name
            user.last_name = last_name
            user.role = role
            user.is_active = is_active
            user.cedula = cedula if cedula else None
            user.telefono = telefono if telefono else None
            user.departamento = departamento if departamento else None
            user.ciudad = ciudad if ciudad else None
            user.can_sell = (role == 'Productor')  # Solo los productores pueden vender por defecto
            
            user.save()
            
            # Manejar la finca si es Productor
            if role == 'Productor':
                from core.models import Farm
                farm = user.farms.first()
                
                if farm:
                    # Actualizar finca existente
                    farm.nombre = finca_nombre
                    farm.departamento = finca_departamento
                    farm.ciudad = finca_ciudad
                    farm.direccion = finca_direccion if finca_direccion else None
                    farm.descripcion = finca_descripcion if finca_descripcion else None
                    farm.area = float(finca_area) if finca_area else None
                    farm.cultivos_principales = finca_cultivos if finca_cultivos else None
                    farm.save()
                else:
                    # Crear nueva finca
                    farm = Farm.objects.create(
                        user=user,
                        nombre=finca_nombre,
                        departamento=finca_departamento,
                        ciudad=finca_ciudad,
                        direccion=finca_direccion if finca_direccion else None,
                        descripcion=finca_descripcion if finca_descripcion else None,
                        area=float(finca_area) if finca_area else None,
                        cultivos_principales=finca_cultivos if finca_cultivos else None,
                        activa=True
                    )
            else:
                # Si cambió de Productor a otro rol, eliminar fincas
                user.farms.all().delete()
            
            messages.success(request, f'Usuario "{user.username}" actualizado exitosamente.')
            return redirect('admin_user_list')
        except Exception as e:
            messages.error(request, f'Error al actualizar el usuario: {str(e)}')
    
    context = {
        'user': user,
        'role_choices': User.ROLE_CHOICES,
        'is_create': False,
        'title': f'Editar Usuario: {user.username}',
    }
    return render(request, 'accounts/admin_user_form.html', context)

@user_passes_test(is_admin)
def admin_user_delete(request, pk):
    """Eliminar usuario"""
    from .admin_audit import log_user_action
    
    user = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        # Registrar la acción antes de eliminar
        log_user_action(
            admin_user=request.user,
            action_type='delete',
            user=user,
            request=request,
            changes={
                'user_id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'fecha_registro': user.date_joined.isoformat() if user.date_joined else None
            }
        )
        
        user.delete()
        messages.success(request, 'Usuario eliminado exitosamente.')
        return redirect('admin_user_list')
    
    context = {'user': user}
    return render(request, 'accounts/admin_user_confirm_delete.html', context)

# Funciones CRUD para cultivos
@user_passes_test(is_admin)
def admin_crop_create(request):
    """Crear cultivo como admin"""
    if request.method == 'POST':
        form = AdminCropForm(request.POST)
        if form.is_valid():
            crop = form.save()
            messages.success(request, f'Cultivo "{crop.nombre}" creado exitosamente para {crop.productor.get_full_name() or crop.productor.username}.')
            return redirect('admin_crop_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AdminCropForm()
    
    context = {
        'form': form,
        'title': 'Crear Nuevo Cultivo',
        'is_create': True,
    }
    return render(request, 'accounts/admin_crop_form.html', context)

@user_passes_test(is_admin)
def admin_crop_edit(request, pk):
    """Editar cultivo como admin"""
    crop = get_object_or_404(Crop, pk=pk)
    
    if request.method == 'POST':
        form = AdminCropForm(request.POST, instance=crop)
        if form.is_valid():
            crop = form.save()
            messages.success(request, f'Cultivo "{crop.nombre}" actualizado exitosamente.')
            return redirect('admin_crop_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AdminCropForm(instance=crop)
    
    context = {
        'form': form,
        'crop': crop,
        'title': f'Editar Cultivo: {crop.nombre}',
        'is_create': False,
    }
    return render(request, 'accounts/admin_crop_form.html', context)

@user_passes_test(is_admin)
def admin_crop_delete(request, pk):
    """Eliminar cultivo"""
    crop = get_object_or_404(Crop, pk=pk)
    if request.method == 'POST':
        crop.delete()
        messages.success(request, 'Cultivo eliminado exitosamente.')
        return redirect('admin_crop_list')
    
    context = {'crop': crop}
    return render(request, 'accounts/admin_crop_confirm_delete.html', context)

# Funciones CRUD para pedidos
@user_passes_test(is_admin)
def admin_order_detail(request, order_id):
    """Detalle de pedido"""
    order = get_object_or_404(Order, id=order_id)
    context = {'order': order}
    return render(request, 'accounts/admin_order_detail.html', context)

@user_passes_test(is_admin)
def admin_order_edit(request, order_id):
    """Editar pedido"""
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        # Lógica para editar pedido
        messages.success(request, 'Pedido actualizado exitosamente.')
        return redirect('admin_order_list')
    
    context = {
        'order': order,
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
    }
    return render(request, 'accounts/admin_order_edit.html', context)

@user_passes_test(is_admin)
def admin_order_delete(request, order_id):
    """Eliminar pedido"""
    from .admin_audit import log_order_action
    
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        # Registrar la acción antes de eliminar
        log_order_action(
            admin_user=request.user,
            action_type='delete',
            order=order,
            request=request,
            changes={
                'order_id': order.id,
                'comprador': order.comprador.username if order.comprador else 'N/A',
                'vendedor': order.vendedor.username if order.vendedor else 'N/A',
                'estado': order.estado,
                'precio_total': str(order.precio_total),
                'fecha_creacion': order.created_at.isoformat() if order.created_at else None
            }
        )
        
        order.delete()
        messages.success(request, 'Pedido eliminado exitosamente.')
        return redirect('admin_order_list')
    
    context = {'order': order}
    return render(request, 'accounts/admin_order_confirm_delete.html', context)

# Funciones CRUD para publicaciones
@user_passes_test(is_admin)
def admin_publication_create(request):
    """Crear publicación como admin"""
    if request.method == 'POST':
        form = AdminPublicationForm(request.POST, request.FILES)
        if form.is_valid():
            publication = form.save()
            messages.success(request, f'Publicación "{publication.cultivo.nombre}" creada exitosamente para {publication.cultivo.productor.get_full_name() or publication.cultivo.productor.username}.')
            return redirect('admin_publication_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AdminPublicationForm()
    
    # Obtener todos los productores para el selector
    producers = User.objects.filter(role='Productor', is_active=True)
    
    context = {
        'form': form,
        'producers': producers,
        'title': 'Crear Nueva Publicación',
        'is_create': True,
    }
    return render(request, 'accounts/admin_publication_form.html', context)

@user_passes_test(is_admin)
def admin_publication_edit(request, pk):
    """Editar publicación como admin"""
    publication = get_object_or_404(Publication, pk=pk)
    
    if request.method == 'POST':
        form = AdminPublicationForm(request.POST, request.FILES, instance=publication)
        if form.is_valid():
            publication = form.save()
            messages.success(request, f'Publicación "{publication.cultivo.nombre}" actualizada exitosamente.')
            return redirect('admin_publication_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AdminPublicationForm(instance=publication)
    
    # Obtener todos los productores para el selector
    producers = User.objects.filter(role='Productor', is_active=True)
    
    context = {
        'form': form,
        'publication': publication,
        'producers': producers,
        'title': f'Editar Publicación: {publication.cultivo.nombre}',
        'is_create': False,
    }
    return render(request, 'accounts/admin_publication_form.html', context)

@user_passes_test(is_admin)
def admin_publication_delete(request, pk):
    """Eliminar publicación"""
    publication = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        publication.delete()
        messages.success(request, 'Publicación eliminada exitosamente.')
        return redirect('admin_publication_list')
    
    context = {'publication': publication}
    return render(request, 'accounts/admin_publication_confirm_delete.html', context)

# Páginas adicionales del admin
@user_passes_test(is_admin)
def admin_history(request):
    """Historial de cambios del admin"""
    from accounts.models import AdminAction
    from django.core.paginator import Paginator
    
    # Obtener acciones del admin
    actions = AdminAction.objects.select_related('admin').order_by('-created_at')
    
    # Filtros
    action_filter = request.GET.get('action_type')
    if action_filter:
        actions = actions.filter(action_type=action_filter)
    
    admin_filter = request.GET.get('admin')
    if admin_filter:
        actions = actions.filter(admin__username=admin_filter)
    
    date_from = request.GET.get('date_from')
    if date_from:
        actions = actions.filter(created_at__date__gte=date_from)
    
    date_to = request.GET.get('date_to')
    if date_to:
        actions = actions.filter(created_at__date__lte=date_to)
    
    # Paginación
    paginator = Paginator(actions, 20)
    page_number = request.GET.get('page')
    actions = paginator.get_page(page_number)
    
    # Obtener administradores para el filtro
    admins = User.objects.filter(role='Admin').values_list('username', flat=True)
    
    context = {
        'actions': actions,
        'action_types': AdminAction.ACTION_TYPES,
        'admins': admins,
        'current_action': action_filter,
        'current_admin': admin_filter,
        'date_from': date_from,
        'date_to': date_to,
    }
    return render(request, 'accounts/admin_history.html', context)

@user_passes_test(is_admin)
def admin_config(request):
    """Configuración del sistema"""
    import subprocess
    import os
    from django.conf import settings
    from django.utils import timezone
    
    # Obtener información real del sistema
    try:
        # Última actualización del repositorio git
        git_log = subprocess.check_output(
            ['git', 'log', '-1', '--format=%cd', '--date=short'],
            cwd=settings.BASE_DIR,
            stderr=subprocess.DEVNULL
        ).decode('utf-8').strip()
        last_commit_date = git_log
    except:
        last_commit_date = timezone.now().strftime('%d %b %Y')
    
    # Información de la base de datos
    db_engine = settings.DATABASES['default']['ENGINE']
    if 'postgresql' in db_engine:
        db_name = 'PostgreSQL'
    elif 'mysql' in db_engine:
        db_name = 'MySQL'
    elif 'sqlite' in db_engine:
        db_name = 'SQLite'
    else:
        db_name = 'Desconocida'
    
    # Estadísticas reales del sistema
    system_stats = {
        'total_users': User.objects.count(),
        'total_crops': Crop.objects.count(),
        'total_publications': Publication.objects.count(),
        'total_orders': Order.objects.count(),
        'active_users': User.objects.filter(is_active=True).count(),
        'admin_users': User.objects.filter(role='Admin').count(),
    }
    
    context = {
        'last_commit_date': last_commit_date,
        'db_name': db_name,
        'system_stats': system_stats,
        'django_version': '4.2.7',  # Puedes obtener esto dinámicamente
        'python_version': os.sys.version.split()[0],
    }
    return render(request, 'accounts/admin_config.html', context)

# Funciones de preview sin autenticación
def admin_history_preview(request):
    """Vista de preview del historial sin autenticación"""
    context = {}
    return render(request, 'accounts/admin_history.html', context)

def admin_config_preview(request):
    """Vista de preview de configuración sin autenticación"""
    context = {}
    return render(request, 'accounts/admin_config.html', context)


@user_passes_test(is_admin)
def admin_get_farms_by_producer(request):
    """Vista AJAX para obtener las fincas de un productor específico"""
    producer_id = request.GET.get('producer_id')
    
    if not producer_id:
        return JsonResponse({'farms': []})
    
    try:
        producer = User.objects.get(id=producer_id, role='Productor')
        farms = Farm.objects.filter(propietario=producer, activa=True)
        
        farms_data = []
        for farm in farms:
            farms_data.append({
                'id': farm.id,
                'nombre': farm.nombre,
                'ciudad': farm.ciudad,
                'departamento': farm.departamento,
                'area_disponible': float(farm.area_disponible)
            })
        
        return JsonResponse({'farms': farms_data})
    except User.DoesNotExist:
        return JsonResponse({'farms': []})


@user_passes_test(is_admin)
def admin_get_crops_by_producer(request):
    """Vista AJAX para obtener los cultivos de un productor específico"""
    producer_id = request.GET.get('producer_id')
    
    if not producer_id:
        return JsonResponse({'crops': []})
    
    try:
        producer = User.objects.get(id=producer_id, role='Productor')
        crops = Crop.objects.filter(productor=producer)
        
        crops_data = []
        for crop in crops:
            crops_data.append({
                'id': crop.id,
                'nombre': crop.nombre,
                'categoria': crop.get_categoria_display(),
                'cantidad_estimada': float(crop.cantidad_estimada),
                'unidad_medida': crop.get_unidad_medida_display(),
                'estado': crop.get_estado_display(),
                'finca_nombre': crop.finca.nombre if crop.finca else 'Sin finca'
            })
        
        return JsonResponse({'crops': crops_data})
    except User.DoesNotExist:
        return JsonResponse({'crops': []})


@user_passes_test(is_admin)
def admin_get_farms_by_crop(request):
    """Vista AJAX para obtener las fincas de un cultivo específico"""
    crop_id = request.GET.get('crop_id')
    
    if not crop_id:
        return JsonResponse({'farms': []})
    
    try:
        crop = Crop.objects.get(id=crop_id)
        farms = Farm.objects.filter(propietario=crop.productor, activa=True)
        
        farms_data = []
        for farm in farms:
            farms_data.append({
                'id': farm.id,
                'nombre': farm.nombre,
                'ciudad': farm.ciudad,
                'departamento': farm.departamento,
                'area_disponible': float(farm.area_disponible)
            })
        
        return JsonResponse({'farms': farms_data})
    except Crop.DoesNotExist:
        return JsonResponse({'farms': []})


# Funciones CRUD para fincas
@user_passes_test(is_admin)
def admin_farm_list(request):
    """Lista de fincas"""
    farms = Farm.objects.select_related('propietario').order_by('-created_at')
    
    # Filtros
    producer_filter = request.GET.get('producer')
    if producer_filter and producer_filter != 'None' and producer_filter.strip():
        farms = farms.filter(propietario_id=producer_filter)
    else:
        producer_filter = None  # Asegurar que sea None si no hay filtro válido
    
    search_query = request.GET.get('search')
    if search_query and search_query != 'None' and search_query.strip():
        farms = farms.filter(
            Q(nombre__icontains=search_query) |
            Q(propietario__username__icontains=search_query) |
            Q(ciudad__icontains=search_query) |
            Q(departamento__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(farms, 20)
    page_number = request.GET.get('page')
    farms = paginator.get_page(page_number)
    
    # Obtener todos los productores para el filtro
    producers = User.objects.filter(role='Productor', is_active=True)
    
    context = {
        'farms': farms,
        'producers': producers,
        'current_producer': producer_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_farm_list_tailadmin.html', context)

@user_passes_test(is_admin)
def admin_farm_create(request):
    """Crear finca como admin"""
    if request.method == 'POST':
        form = AdminFarmForm(request.POST)
        if form.is_valid():
            farm = form.save()
            messages.success(request, f'Finca "{farm.nombre}" creada exitosamente.')
            return redirect('admin_farm_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AdminFarmForm()
    
    context = {
        'form': form,
        'title': 'Crear Nueva Finca',
        'is_create': True,
    }
    return render(request, 'accounts/admin_farm_form.html', context)

@user_passes_test(is_admin)
def admin_farm_edit(request, pk):
    """Editar finca como admin"""
    farm = get_object_or_404(Farm, pk=pk)
    
    if request.method == 'POST':
        form = AdminFarmForm(request.POST, instance=farm)
        if form.is_valid():
            farm = form.save()
            messages.success(request, f'Finca "{farm.nombre}" actualizada exitosamente.')
            return redirect('admin_farm_list')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = AdminFarmForm(instance=farm)
    
    context = {
        'form': form,
        'farm': farm,
        'title': f'Editar Finca: {farm.nombre}',
        'is_create': False,
    }
    return render(request, 'accounts/admin_farm_form.html', context)

@user_passes_test(is_admin)
def admin_farm_delete(request, pk):
    """Eliminar finca"""
    farm = get_object_or_404(Farm, pk=pk)
    
    if request.method == 'POST':
        farm_name = farm.nombre
        farm.delete()
        messages.success(request, f'Finca "{farm_name}" eliminada exitosamente.')
        return redirect('admin_farm_list')
    
    context = {
        'farm': farm,
    }
    return render(request, 'accounts/admin_farm_confirm_delete.html', context)


# Funciones CRUD para conversaciones/chats
@user_passes_test(is_admin)
def admin_conversation_list(request):
    """Lista de todas las conversaciones del sistema"""
    conversations = Conversation.objects.select_related('publication').prefetch_related('participants', 'messages__sender').order_by('-updated_at')
    
    # Filtros
    user_filter = request.GET.get('user')
    if user_filter and user_filter != 'None' and user_filter.strip():
        conversations = conversations.filter(participants__id=user_filter)
    else:
        user_filter = None  # Asegurar que sea None si no hay filtro válido
    
    search_query = request.GET.get('search')
    if search_query and search_query != 'None' and search_query.strip():
        conversations = conversations.filter(
            Q(participants__username__icontains=search_query) |
            Q(participants__email__icontains=search_query) |
            Q(participants__first_name__icontains=search_query) |
            Q(participants__last_name__icontains=search_query) |
            (Q(publication__isnull=False) & Q(publication__titulo__icontains=search_query))
        )
    
    # Paginación
    paginator = Paginator(conversations, 20)
    page_number = request.GET.get('page')
    conversations = paginator.get_page(page_number)
    
    # Obtener todos los usuarios para el filtro
    users = User.objects.filter(is_active=True).order_by('username')
    
    context = {
        'conversations': conversations,
        'users': users,
        'current_user': user_filter,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_conversation_list_tailadmin.html', context)

@user_passes_test(is_admin)
def admin_conversation_detail(request, pk):
    """Detalle de una conversación específica para el admin"""
    conversation = get_object_or_404(Conversation.objects.prefetch_related('messages__sender', 'participants'), pk=pk)
    
    # Obtener los participantes
    participants = conversation.participants.all()
    buyer = None
    seller = None
    
    if conversation.publication:
        seller = conversation.publication.cultivo.productor
        buyer = participants.exclude(id=seller.id).first()
    else:
        # Si no hay publicación asociada, tomar los dos participantes
        buyer = participants.first()
        seller = participants.last()
    
    # Obtener mensajes
    messages = conversation.messages.all().order_by('created_at')
    
    context = {
        'conversation': conversation,
        'messages': messages,
        'buyer': buyer,
        'seller': seller,
        'participants': participants,
    }
    
    return render(request, 'accounts/admin_conversation_detail.html', context)

@user_passes_test(is_admin)
def admin_conversation_delete(request, pk):
    """Eliminar conversación"""
    conversation = get_object_or_404(Conversation, pk=pk)
    
    if request.method == 'POST':
        # Obtener información antes de eliminar
        participants = list(conversation.participants.all())
        message_count = conversation.messages.count()
        
        conversation.delete()
        
        messages.success(request, f'Conversación eliminada exitosamente. Se eliminaron {message_count} mensajes.')
        return redirect('admin_conversation_list')
    
    # Obtener información para mostrar
    participants = conversation.participants.all()
    message_count = conversation.messages.count()
    last_message = conversation.messages.last()
    
    context = {
        'conversation': conversation,
        'participants': participants,
        'message_count': message_count,
        'last_message': last_message,
    }
    
    return render(request, 'accounts/admin_conversation_confirm_delete.html', context)


@user_passes_test(is_admin)
def admin_audit_log(request):
    """Historial de acciones del administrador"""
    # Filtros
    action_type = request.GET.get('action_type', '')
    object_type = request.GET.get('object_type', '')
    search_query = request.GET.get('search', '')
    
    # Obtener acciones
    actions = AdminAction.objects.select_related('admin').all()
    
    # Aplicar filtros
    if action_type:
        actions = actions.filter(action_type=action_type)
    
    if object_type:
        actions = actions.filter(object_type=object_type)
    
    if search_query and search_query.strip():
        actions = actions.filter(
            Q(object_name__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(admin__username__icontains=search_query)
        )
    
    # Paginación
    paginator = Paginator(actions, 25)  # 25 acciones por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    stats = {
        'total_actions': AdminAction.objects.count(),
        'actions_today': AdminAction.objects.filter(created_at__date=timezone.now().date()).count(),
        'actions_this_week': AdminAction.objects.filter(
            created_at__date__gte=timezone.now().date() - timedelta(days=7)
        ).count(),
        'most_active_admin': AdminAction.objects.values('admin__username').annotate(
            count=Count('id')
        ).order_by('-count').first(),
    }
    
    context = {
        'page_obj': page_obj,
        'actions': page_obj,
        'stats': stats,
        'action_types': AdminAction.ACTION_TYPES,
        'object_types': AdminAction.OBJECT_TYPES,
        'current_action_type': action_type,
        'current_object_type': object_type,
        'search_query': search_query,
    }
    
    return render(request, 'accounts/admin_audit_log.html', context)
