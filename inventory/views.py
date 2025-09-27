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
    """Panel de ventas para productores"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('index')
    
    # Todas las órdenes del productor
    orders = Order.objects.filter(
        publicacion__cultivo__productor=request.user
    ).select_related('publicacion__cultivo', 'comprador').order_by('-created_at')
    
    # Estadísticas
    total_sales = orders.filter(estado='entregado').aggregate(total=Sum('precio_total'))['total'] or 0
    pending_orders = orders.filter(estado='confirmado').count()
    completed_orders = orders.filter(estado='entregado').count()
    
    context = {
        'orders': orders,
        'total_sales': total_sales,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
    }
    return render(request, 'inventory/producer_sales.html', context)