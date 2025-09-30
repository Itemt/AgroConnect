from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from .models import Publication
from inventory.models import Crop, Product
from .forms import PublicationForm
from accounts.models import User

# Create your views here.

def marketplace_view(request):
    """Vista principal del marketplace"""
    publications = Publication.objects.filter(
        estado='disponible', 
        cantidad_disponible__gt=0
    ).select_related(
        'cultivo__productor__producer_profile', 
        'cultivo__producto'
    ).order_by('-created_at')
    
    # Obtener todas las categorías disponibles
    categorias = Product.CATEGORIA_CHOICES
    
    # Filtros de búsqueda
    search_query = request.GET.get('search', '')
    categoria_filter = request.GET.get('categoria', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    ubicacion_filter = request.GET.get('ubicacion', '')
    orden = request.GET.get('orden', '-created_at')
    
    # Aplicar filtros
    if search_query:
        publications = publications.filter(
            Q(cultivo__producto__nombre__icontains=search_query) |
            Q(cultivo__productor__first_name__icontains=search_query) |
            Q(cultivo__productor__last_name__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    # Filtrar por categoría
    if categoria_filter:
        publications = publications.filter(cultivo__producto__categoria=categoria_filter)
    
    # Filtrar por rango de precios
    if precio_min:
        try:
            publications = publications.filter(precio_por_unidad__gte=float(precio_min))
        except ValueError:
            pass
    
    if precio_max:
        try:
            publications = publications.filter(precio_por_unidad__lte=float(precio_max))
        except ValueError:
            pass
    
    # Filtrar por ubicación
    if ubicacion_filter:
        publications = publications.filter(
            cultivo__productor__producer_profile__location__icontains=ubicacion_filter
        )
    
    # Ordenar resultados
    valid_orders = ['-created_at', 'precio_por_unidad', '-precio_por_unidad', 'cultivo__producto__nombre']
    if orden in valid_orders:
        publications = publications.order_by(orden)
    
    # Obtener ubicaciones únicas para el filtro
    ubicaciones = publications.values_list(
        'cultivo__productor__producer_profile__location', flat=True
    ).distinct().exclude(cultivo__productor__producer_profile__location__isnull=True)
    
    # Convertir a lista para poder agregar atributos dinámicos
    publications_list = list(publications)
    
    # Procesar ubicación para cada publicación (la categoría ya viene en la consulta)
    for publication in publications_list:
        # Procesar ubicación para mostrar solo ciudad/región
        try:
            if publication.cultivo.productor.producer_profile and publication.cultivo.productor.producer_profile.location:
                location = publication.cultivo.productor.producer_profile.location
                # Extraer ciudad (asumiendo formato "Calle, Ciudad, País" o similar)
                location_parts = [part.strip() for part in location.split(',')]
                if len(location_parts) > 1:
                    # Tomar la segunda parte (ciudad) y la primera (calle/sector)
                    publication.ciudad_display = f"{location_parts[1][:20]}, {location_parts[0][:15]}"
                else:
                    publication.ciudad_display = location[:25]
            else:
                publication.ciudad_display = "Ubicación no especificada"
        except User.producer_profile.RelatedObjectDoesNotExist:
            publication.ciudad_display = "Productor sin perfil"
    
    context = {
        'publications': publications_list,
        'search_query': search_query,
        'categorias': categorias,
        'categoria_filter': categoria_filter,
        'precio_min': precio_min,
        'precio_max': precio_max,
        'ubicacion_filter': ubicacion_filter,
        'ubicaciones': ubicaciones,
        'orden': orden,
        'total_productos': len(publications_list),
    }
    return render(request, 'marketplace/marketplace.html', context)

def publication_detail_view(request, publication_id):
    """Detalle de una publicación"""
    publication = get_object_or_404(
        Publication.objects.select_related(
            'cultivo__productor__producer_profile', 
            'cultivo__producto'
        ), 
        pk=publication_id
    )
    
    # Procesar ubicación para mostrar solo ciudad/región
    try:
        if publication.cultivo.productor.producer_profile and publication.cultivo.productor.producer_profile.location:
            location = publication.cultivo.productor.producer_profile.location
            location_parts = [part.strip() for part in location.split(',')]
            if len(location_parts) > 1:
                publication.ciudad_display = f"{location_parts[1][:25]}, {location_parts[0][:20]}"
            else:
                publication.ciudad_display = location[:30]
        else:
            publication.ciudad_display = "Ubicación no especificada"
    except User.producer_profile.RelatedObjectDoesNotExist:
        publication.ciudad_display = "Productor sin perfil"
    
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
    
    crop = get_object_or_404(Crop.objects.select_related('producto'), pk=crop_id, productor=request.user)
    
    # Verificar si ya existe una publicación disponible para este cultivo
    existing_publication = Publication.objects.filter(cultivo=crop, estado='disponible').first()
    if existing_publication:
        messages.info(request, 'Este cultivo ya tiene una publicación disponible.')
        return redirect('publication_edit', pk=existing_publication.pk)

    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.cultivo = crop
            publication.save()
            messages.success(request, 'Publicación creada exitosamente.')
            return redirect('producer_dashboard')
    else:
        form = PublicationForm(user=request.user, initial={
            'cantidad_disponible': crop.cantidad_estimada,
            'categoria': crop.producto.categoria,
            'ciudad': request.user.producer_profile.ciudad if hasattr(request.user, 'producer_profile') else ''
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
    publication = get_object_or_404(Publication, pk=pk, cultivo__productor=request.user)
    
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, instance=publication, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publicación actualizada exitosamente.')
            return redirect('producer_dashboard')
    else:
        form = PublicationForm(instance=publication, user=request.user)
    
    context = {
        'form': form,
        'publication': publication,
        'title': 'Editar Publicación'
    }
    return render(request, 'marketplace/publication_form.html', context)

@login_required
def publication_delete_view(request, pk):
    """Eliminar publicación"""
    publication = get_object_or_404(Publication, pk=pk, cultivo__productor=request.user)
    
    if request.method == 'POST':
        publication.estado = 'agotado'
        publication.save()
        messages.success(request, 'Publicación marcada como agotada exitosamente.')
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
        cultivo__productor=request.user
    ).select_related('cultivo').order_by('-created_at')
    
    context = {
        'publications': publications
    }
    return render(request, 'marketplace/my_publications.html', context)