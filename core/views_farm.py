from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from .models import Farm
from .forms import FarmForm
from .colombia_locations import get_departments
from inventory.models import Crop

@login_required
def farm_list(request):
    """Lista de fincas del usuario"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('index')
    
    fincas = Farm.objects.filter(propietario=request.user).order_by('-created_at')
    
    context = {
        'fincas': fincas,
    }
    return render(request, 'core/farm_list.html', context)

@login_required
def farm_detail(request, pk):
    """Detalle de una finca específica"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('index')
    
    finca = get_object_or_404(Farm, pk=pk, propietario=request.user)
    cultivos = Crop.objects.filter(finca=finca).order_by('-created_at')
    
    context = {
        'finca': finca,
        'cultivos': cultivos,
    }
    return render(request, 'core/farm_detail.html', context)

@login_required
def farm_create(request):
    """Crear nueva finca"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('index')
    
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            finca = form.save(commit=False)
            finca.propietario = request.user
            finca.save()
            messages.success(request, f'Finca "{finca.nombre}" creada exitosamente.')
            return redirect('core:farm_detail', pk=finca.pk)
    else:
        form = FarmForm()
    
    context = {
        'form': form,
        'title': 'Crear Nueva Finca',
        'departments_list': [d[0] for d in get_departments()],
    }
    return render(request, 'core/farm_form.html', context)

@login_required
def farm_edit(request, pk):
    """Editar finca existente"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('index')
    
    finca = get_object_or_404(Farm, pk=pk, propietario=request.user)
    
    if request.method == 'POST':
        form = FarmForm(request.POST, instance=finca)
        if form.is_valid():
            form.save()
            messages.success(request, f'Finca "{finca.nombre}" actualizada exitosamente.')
            return redirect('core:farm_detail', pk=finca.pk)
    else:
        form = FarmForm(instance=finca)
    
    context = {
        'form': form,
        'finca': finca,
        'title': f'Editar Finca: {finca.nombre}',
        'departments_list': [d[0] for d in get_departments()],
    }
    return render(request, 'core/farm_form.html', context)

@login_required
def farm_delete(request, pk):
    """Eliminar finca con eliminación en cascada"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('index')
    
    finca = get_object_or_404(Farm, pk=pk, propietario=request.user)
    
    if request.method == 'POST':
        # Obtener información antes de eliminar para el mensaje
        nombre_finca = finca.nombre
        cultivos_count = finca.cultivos.count()
        
        # Eliminar la finca (esto eliminará automáticamente los cultivos por CASCADE)
        finca.delete()
        
        # Mensaje de confirmación con detalles
        if cultivos_count > 0:
            messages.success(request, f'Finca "{nombre_finca}" y sus {cultivos_count} cultivo(s) eliminados exitosamente.')
        else:
            messages.success(request, f'Finca "{nombre_finca}" eliminada exitosamente.')
        
        return redirect('core:farm_list')
    
    context = {
        'finca': finca,
    }
    return render(request, 'core/farm_confirm_delete.html', context)

@csrf_exempt
def get_ciudades(request):
    """AJAX endpoint para obtener ciudades de un departamento"""
    try:
        departamento = request.POST.get('departamento')
        logger.info("Getting cities for department")
        logger.info(f"Departamento recibido: {departamento}")
        
        if not departamento:
            logger.warning("No se recibió departamento")
            return JsonResponse({'ciudades': []})
        
        from .colombia_locations import get_cities_by_department
        
        ciudades = get_cities_by_department(departamento)
        logger.info(f"Ciudades encontradas: {len(ciudades)}")
        
        ciudades_options = [{'value': ciudad[0], 'text': ciudad[1]} for ciudad in ciudades]
        logger.info(f"Opciones de ciudades: {ciudades_options[:3]}...")  # Mostrar solo las primeras 3
        
        return JsonResponse({'ciudades': ciudades_options})
        
    except Exception as e:
        logger.error(f"Error en get_ciudades: {str(e)}")
        return JsonResponse({'error': str(e), 'ciudades': []}, status=500)
