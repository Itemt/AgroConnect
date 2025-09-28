from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count, Q
from .models import Crop, Product
from .forms import CropForm
from marketplace.models import Publication
from sales.models import Order

# Create your views here.

@login_required
def producer_dashboard(request):
    """Dashboard principal para productores"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('index')
    
    # Estadísticas del productor
    total_crops = request.user.cultivos.count()
    active_publications = Publication.objects.filter(cultivo__productor=request.user, estado='disponible').count()
    total_orders = Order.objects.filter(publicacion__cultivo__productor=request.user).count()
    total_revenue = Order.objects.filter(
        publicacion__cultivo__productor=request.user,
        estado='entregado'
    ).aggregate(total=Sum('precio_total'))['total'] or 0
    
    # Cultivos recientes
    recent_crops = request.user.cultivos.order_by('-created_at')[:5]
    
    # Pedidos recientes
    recent_orders = Order.objects.filter(
        publicacion__cultivo__productor=request.user
    ).select_related('publicacion__cultivo', 'comprador').order_by('-created_at')[:5]
    
    context = {
        'total_crops': total_crops,
        'active_publications': active_publications,
        'total_orders': total_orders,
        'total_revenue': total_revenue,
        'recent_crops': recent_crops,
        'recent_orders': recent_orders,
    }
    return render(request, 'inventory/producer_dashboard.html', context)

@login_required
def crop_list_view(request):
    """Lista de cultivos del productor"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('index')
    
    crops = request.user.cultivos.order_by('-created_at')
    
    context = {
        'crops': crops
    }
    return render(request, 'inventory/crop_list.html', context)

@login_required
def crop_create_view(request):
    """Crear nuevo cultivo"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('index')
    
    if request.method == 'POST':
        form = CropForm(request.POST)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.productor = request.user
            crop.save()
            messages.success(request, 'Cultivo creado exitosamente.')
            return redirect('crop_list')
    else:
        form = CropForm()
    
    context = {
        'form': form,
        'title': 'Agregar Nuevo Cultivo'
    }
    return render(request, 'inventory/crop_form.html', context)

@login_required
def crop_update_view(request, pk):
    """Editar cultivo existente"""
    crop = get_object_or_404(Crop, pk=pk, productor=request.user)
    
    if request.method == 'POST':
        form = CropForm(request.POST, instance=crop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cultivo actualizado exitosamente.')
            return redirect('crop_list')
    else:
        form = CropForm(instance=crop)
    
    context = {
        'form': form,
        'crop': crop,
        'title': 'Editar Cultivo'
    }
    return render(request, 'inventory/crop_form.html', context)

@login_required
def crop_delete_view(request, pk):
    """Eliminar cultivo"""
    crop = get_object_or_404(Crop, pk=pk, productor=request.user)
    
    if request.method == 'POST':
        crop.delete()
        messages.success(request, 'Cultivo eliminado exitosamente.')
        return redirect('crop_list')
    
    context = {
        'crop': crop
    }
    return render(request, 'inventory/crop_confirm_delete.html', context)

@login_required
def producer_sales_view(request):
    """Panel de ventas mejorado para productores"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('index')
    
    # Obtener o crear perfil de estadísticas
    from sales.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    if not created:
        profile.actualizar_estadisticas_vendedor()
    
    # Filtros de búsqueda
    from sales.forms import OrderSearchForm
    form = OrderSearchForm(request.GET)
    
    # Todas las órdenes del productor
    orders = Order.objects.filter(
        publicacion__cultivo__productor=request.user
    ).select_related('publicacion__cultivo', 'comprador')
    
    # Aplicar filtros
    if form.is_valid():
        search = form.cleaned_data.get('search')
        estado = form.cleaned_data.get('estado')
        fecha_desde = form.cleaned_data.get('fecha_desde')
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        
        if search:
            orders = orders.filter(
                Q(publicacion__cultivo__nombre_producto__icontains=search) |
                Q(comprador__first_name__icontains=search) |
                Q(comprador__last_name__icontains=search)
            )
        
        if estado:
            orders = orders.filter(estado=estado)
        
        if fecha_desde:
            orders = orders.filter(created_at__date__gte=fecha_desde)
        
        if fecha_hasta:
            orders = orders.filter(created_at__date__lte=fecha_hasta)
    
    # Agregar acciones disponibles para cada pedido
    orders_with_actions = []
    for order in orders.order_by('-created_at'):
        order.available_actions = order.get_available_actions_for_user(request.user)
        orders_with_actions.append(order)
    
    # Estadísticas detalladas
    total_orders = orders.count()
    pending_orders = orders.filter(estado__in=['pendiente', 'confirmado']).count()
    in_progress_orders = orders.filter(estado__in=['en_preparacion', 'enviado', 'en_transito']).count()
    delivered_orders = orders.filter(estado='entregado').count()
    completed_orders = orders.filter(estado='completado').count()
    cancelled_orders = orders.filter(estado='cancelado').count()
    
    # Ingresos
    total_revenue = orders.filter(estado='completado').aggregate(total=Sum('precio_total'))['total'] or 0
    pending_revenue = orders.filter(estado__in=['confirmado', 'en_preparacion', 'enviado', 'en_transito', 'entregado']).aggregate(total=Sum('precio_total'))['total'] or 0
    
    # Estadísticas por producto
    product_stats = orders.filter(estado='completado').values(
        'publicacion__cultivo__nombre_producto'
    ).annotate(
        total_vendido=Sum('cantidad_acordada'),
        total_ingresos=Sum('precio_total'),
        num_pedidos=Count('id')
    ).order_by('-total_ingresos')[:5]
    
    # Estadísticas por mes (últimos 6 meses)
    from datetime import datetime, timedelta
    from django.db.models.functions import TruncMonth
    
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_stats = orders.filter(
        created_at__gte=six_months_ago,
        estado='completado'
    ).annotate(
        month=TruncMonth('created_at')
    ).values('month').annotate(
        total_ventas=Count('id'),
        total_ingresos=Sum('precio_total')
    ).order_by('month')
    
    # Top compradores
    top_buyers = orders.filter(estado='completado').values(
        'comprador__first_name', 'comprador__last_name', 'comprador__id'
    ).annotate(
        total_pedidos=Count('id'),
        total_gastado=Sum('precio_total')
    ).order_by('-total_gastado')[:5]
    
    # Pedidos que requieren atención
    orders_need_attention = orders.filter(
        estado__in=['pendiente', 'confirmado', 'en_preparacion']
    ).order_by('created_at')[:10]
    
    # Agregar acciones a pedidos que necesitan atención
    for order in orders_need_attention:
        order.available_actions = order.get_available_actions_for_user(request.user)
    
    # Calificaciones recientes
    from sales.models import Rating
    recent_ratings = Rating.objects.filter(
        calificado=request.user
    ).select_related('calificador', 'pedido').order_by('-created_at')[:5]
    
    # Paginación para todos los pedidos
    from django.core.paginator import Paginator
    paginator = Paginator(orders_with_actions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'orders': page_obj,
        'form': form,
        'profile': profile,
        
        # Estadísticas generales
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'in_progress_orders': in_progress_orders,
        'delivered_orders': delivered_orders,
        'completed_orders': completed_orders,
        'cancelled_orders': cancelled_orders,
        
        # Ingresos
        'total_revenue': total_revenue,
        'pending_revenue': pending_revenue,
        
        # Estadísticas detalladas
        'product_stats': product_stats,
        'monthly_stats': monthly_stats,
        'top_buyers': top_buyers,
        'orders_need_attention': orders_need_attention,
        'recent_ratings': recent_ratings,
        
        # Métricas calculadas
        'avg_order_value': total_revenue / completed_orders if completed_orders > 0 else 0,
        'completion_rate': (completed_orders / total_orders * 100) if total_orders > 0 else 0,
        'cancellation_rate': (cancelled_orders / total_orders * 100) if total_orders > 0 else 0,
    }
    return render(request, 'inventory/producer_sales.html', context)