from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Publication
from inventory.models import Crop
from .forms import PublicationForm

# Create your views here.

def marketplace_view(request):
    """Vista principal del marketplace"""
    publications = Publication.objects.filter(
        status='disponible', 
        available_quantity__gt=0
    ).select_related('crop__product', 'crop__producer').order_by('-created_at')
    
    # Filtros de búsqueda
    search_query = request.GET.get('search', '')
    if search_query:
        publications = publications.filter(
            Q(crop__product__name__icontains=search_query) |
            Q(crop__producer__first_name__icontains=search_query) |
            Q(crop__producer__last_name__icontains=search_query)
        )
    
    context = {
        'publications': publications,
        'search_query': search_query,
    }
    return render(request, 'marketplace/marketplace.html', context)

def publication_detail_view(request, publication_id):
    """Detalle de una publicación"""
    publication = get_object_or_404(
        Publication.objects.select_related('crop__product', 'crop__producer'), 
        pk=publication_id
    )
    context = {
        'publication': publication
    }
    return render(request, 'marketplace/publication_detail.html', context)

@login_required
def publication_create_view(request, crop_id):
    """Crear nueva publicación"""
    if request.user.role != 'Productor':
        messages.error(request, 'Solo los productores pueden crear publicaciones.')
        return redirect('marketplace')
    
    crop = get_object_or_404(Crop, pk=crop_id, producer=request.user)
    
    # Verificar si ya existe una publicación disponible para este cultivo
    existing_publication = Publication.objects.filter(crop=crop, status='disponible').first()
    if existing_publication:
        messages.info(request, 'Este cultivo ya tiene una publicación disponible.')
        return redirect('publication_edit', pk=existing_publication.pk)

    if request.method == 'POST':
        form = PublicationForm(request.POST)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.crop = crop
            publication.save()
            messages.success(request, 'Publicación creada exitosamente.')
            return redirect('producer_dashboard')
    else:
        # Pre-llenar el formulario con datos del cultivo
        form = PublicationForm(initial={
            'available_quantity': crop.estimated_quantity,
        })

    context = {
        'form': form,
        'crop': crop,
        'title': 'Crear Publicación'
    }
    return render(request, 'marketplace/publication_form.html', context)

@login_required
def publication_edit_view(request, pk):
    """Editar publicación existente"""
    publication = get_object_or_404(Publication, pk=pk, crop__producer=request.user)
    
    if request.method == 'POST':
        form = PublicationForm(request.POST, instance=publication)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publicación actualizada exitosamente.')
            return redirect('producer_dashboard')
    else:
        form = PublicationForm(instance=publication)
    
    context = {
        'form': form,
        'publication': publication,
        'title': 'Editar Publicación'
    }
    return render(request, 'marketplace/publication_form.html', context)

@login_required
def publication_delete_view(request, pk):
    """Eliminar publicación"""
    publication = get_object_or_404(Publication, pk=pk, crop__producer=request.user)
    
    if request.method == 'POST':
        publication.status = 'caducado'
        publication.save()
        messages.success(request, 'Publicación marcada como caducada exitosamente.')
        return redirect('producer_dashboard')
    
    context = {
        'publication': publication
    }
    return render(request, 'marketplace/publication_confirm_delete.html', context)

@login_required
def my_publications_view(request):
    """Lista de publicaciones del productor"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('marketplace')
    
    publications = Publication.objects.filter(
        crop__producer=request.user
    ).select_related('crop__product').order_by('-created_at')
    
    context = {
        'publications': publications
    }
    return render(request, 'marketplace/my_publications.html', context)