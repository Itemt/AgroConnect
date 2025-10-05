from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .models import Farm
from .forms_farm import FarmForm
from core.colombia_locations import get_cities_by_department


@login_required
def farm_list(request):
    """Lista de fincas del usuario"""
    farms = Farm.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'farms': farms,
    }
    return render(request, 'accounts/farm_list.html', context)


@login_required
def farm_create(request):
    """Crear una nueva finca"""
    if request.method == 'POST':
        form = FarmForm(request.POST)
        if form.is_valid():
            farm = form.save(commit=False)
            farm.user = request.user
            farm.save()
            messages.success(request, f'Finca "{farm.nombre}" creada exitosamente.')
            return redirect('farm_list')
    else:
        form = FarmForm()
    
    context = {
        'form': form,
        'title': 'Agregar Nueva Finca',
        'button_text': 'Crear Finca'
    }
    return render(request, 'accounts/farm_form.html', context)


@login_required
def farm_edit(request, farm_id):
    """Editar una finca existente"""
    farm = get_object_or_404(Farm, pk=farm_id, user=request.user)
    
    if request.method == 'POST':
        form = FarmForm(request.POST, instance=farm)
        if form.is_valid():
            form.save()
            messages.success(request, f'Finca "{farm.nombre}" actualizada exitosamente.')
            return redirect('farm_list')
    else:
        form = FarmForm(instance=farm)
    
    context = {
        'form': form,
        'farm': farm,
        'title': f'Editar Finca: {farm.nombre}',
        'button_text': 'Guardar Cambios'
    }
    return render(request, 'accounts/farm_form.html', context)


@login_required
def farm_delete(request, farm_id):
    """Eliminar una finca"""
    farm = get_object_or_404(Farm, pk=farm_id, user=request.user)
    
    # Verificar si la finca tiene cultivos asociados
    cultivos_count = farm.cultivos.count()
    
    if request.method == 'POST':
        farm_name = farm.nombre
        farm.delete()
        messages.success(request, f'Finca "{farm_name}" eliminada exitosamente.')
        return redirect('farm_list')
    
    context = {
        'farm': farm,
        'cultivos_count': cultivos_count
    }
    return render(request, 'accounts/farm_confirm_delete.html', context)


@login_required
def get_farm_cities_ajax(request):
    """Vista AJAX para obtener ciudades de un departamento para fincas"""
    departamento = request.GET.get('departamento', None)
    if departamento:
        cities = get_cities_by_department(departamento)
        return JsonResponse({'cities': cities})
    return JsonResponse({'cities': []})
