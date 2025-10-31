from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Publication, PublicationImage
from .forms import PublicationForm
from inventory.models import Crop
from accounts.models import User, ProducerProfile
from django.db.models import Q, Max
from django.core.paginator import Paginator

# Create your views here.

def marketplace_view(request):
    """Vista principal del marketplace"""
    publications = Publication.objects.filter(
        estado='Activa', 
        cantidad_disponible__gt=0
    ).select_related(
        'cultivo__productor__producer_profile'
    ).order_by('-created_at')
    
    # Obtener todas las categorías disponibles
    categorias = Crop.CATEGORIA_CHOICES # Changed from Product.CATEGORIA_CHOICES
    
    # Filtros de búsqueda
    search_query = request.GET.get('search', '')
    categoria_filter = request.GET.get('categoria', '')
    precio_min = request.GET.get('precio_min', '')
    precio_max = request.GET.get('precio_max', '')
    ubicacion_filter = request.GET.get('ubicacion', '')
    vendedor_filter = request.GET.get('vendedor', '')
    orden = request.GET.get('orden', '-created_at')
    
    # Aplicar filtros
    if search_query:
        publications = publications.filter(
            Q(cultivo__nombre__icontains=search_query) |
            Q(cultivo__productor__first_name__icontains=search_query) |
            Q(cultivo__productor__last_name__icontains=search_query) |
            Q(descripcion__icontains=search_query)
        )
    
    # Filtrar por categoría
    if categoria_filter:
        publications = publications.filter(cultivo__categoria=categoria_filter)
    
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
    
    # Filtrar por vendedor
    if vendedor_filter:
        publications = publications.filter(
            Q(cultivo__productor__username__icontains=vendedor_filter) |
            Q(cultivo__productor__first_name__icontains=vendedor_filter) |
            Q(cultivo__productor__last_name__icontains=vendedor_filter)
        )
    
    # Ordenar resultados
    valid_orders = ['-created_at', 'precio_por_unidad', '-precio_por_unidad', 'cultivo__nombre']
    if orden in valid_orders:
        publications = publications.order_by(orden)
    
    # Obtener ubicaciones únicas para el filtro
    ubicaciones = publications.values_list(
        'cultivo__productor__producer_profile__location', flat=True
    ).distinct().exclude(cultivo__productor__producer_profile__location__isnull=True)
    
    # Convertir a lista para poder agregar atributos dinámicos
    publications_list = list(publications)
    
    # Si el usuario está autenticado, mover sus propios productos al final
    if request.user.is_authenticated:
        own_publications = [p for p in publications_list if p.cultivo.productor == request.user]
        other_publications = [p for p in publications_list if p.cultivo.productor != request.user]
        publications_list = other_publications + own_publications
    
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
                    publication.display_location = f"{location_parts[1][:20]}, {location_parts[0][:15]}"
                else:
                    publication.display_location = location[:25]
            else:
                publication.display_location = "Ubicación no especificada"
        except ProducerProfile.DoesNotExist:
            publication.display_location = "Productor sin perfil"
    
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
            'cultivo__productor__producer_profile'
        ), 
        pk=publication_id
    )
    
    # Procesar ubicación para mostrar solo ciudad/región
    try:
        if publication.cultivo.productor.producer_profile and publication.cultivo.productor.producer_profile.location:
            location = publication.cultivo.productor.producer_profile.location
            location_parts = [part.strip() for part in location.split(',')]
            if len(location_parts) > 1:
                publication.display_location = f"{location_parts[1][:25]}, {location_parts[0][:20]}"
            else:
                publication.display_location = location[:30]
        else:
            publication.display_location = "Ubicación no especificada"
    except ProducerProfile.DoesNotExist:
        publication.display_location = "Productor sin perfil"
    
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
    
    crop = get_object_or_404(Crop, pk=crop_id, productor=request.user)
    
    # Verificar si ya existe una publicación activa para este cultivo
    existing_publication = Publication.objects.filter(cultivo=crop, estado='Activa').first()
    if existing_publication:
        messages.info(request, 'Este cultivo ya tiene una publicación activa.')
        return redirect('publication_edit', pk=existing_publication.pk)

    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES, user=request.user, crop=crop)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.cultivo = crop
            # Establecer ubicación automáticamente desde la finca
            if crop.finca:
                publication.departamento = crop.finca.departamento
                publication.ciudad = crop.finca.ciudad
            publication.save()
            
            # Manejar múltiples imágenes
            images = request.FILES.getlist('images')
            if images:
                # Limitar a 10 imágenes
                images = images[:10]
                for index, image in enumerate(images):
                    PublicationImage.objects.create(
                        publication=publication,
                        image=image,
                        is_primary=(index == 0),  # La primera es la principal
                        order=index
                    )
            
            messages.success(request, 'Publicación creada exitosamente.')
            return redirect('producer_dashboard')
    else:
        form = PublicationForm(user=request.user, crop=crop, initial={
            'cantidad_disponible': crop.cantidad_estimada,
            'categoria': crop.categoria,
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
            
            # Manejar nuevas imágenes
            images = request.FILES.getlist('images')
            if images:
                # Limitar a 10 imágenes totales
                current_images_count = publication.images.count()
                max_new_images = 10 - current_images_count
                
                if max_new_images > 0:
                    images = images[:max_new_images]
                    # Obtener el último orden
                    last_order = publication.images.aggregate(max_order=Max('order'))['max_order'] or -1
                    
                    for index, image in enumerate(images):
                        PublicationImage.objects.create(
                            publication=publication,
                            image=image,
                            is_primary=(current_images_count == 0 and index == 0),  # Solo si no hay imágenes
                            order=last_order + index + 1
                        )
            
            messages.success(request, 'Publicación actualizada exitosamente.')
            return redirect('producer_dashboard')
    else:
        form = PublicationForm(instance=publication, user=request.user)
    
    context = {
        'form': form,
        'publication': publication,
        'title': 'Editar Publicación',
        'existing_images': publication.images.all().order_by('order')
    }
    return render(request, 'marketplace/publication_form.html', context)

@login_required
def publication_delete_view(request, pk):
    """Eliminar publicación"""
    publication = get_object_or_404(Publication, pk=pk, cultivo__productor=request.user)
    
    if request.method == 'POST':
        # Guardar el nombre del cultivo antes de eliminar
        cultivo_nombre = publication.cultivo.nombre
        # Eliminar la publicación permanentemente
        publication.delete()
        messages.success(request, f'Publicación de {cultivo_nombre} eliminada exitosamente.')
        return redirect('my_publications')
    
    context = {
        'publication': publication
    }
    return render(request, 'marketplace/publication_confirm_delete.html', context)

@login_required
def select_crop_for_publication_view(request):
    """Seleccionar cultivo para crear publicación"""
    if request.user.role != 'Productor':
        messages.error(request, 'Acceso denegado. Solo para productores.')
        return redirect('marketplace')
    
    # Obtener todos los cultivos del usuario para debug
    all_crops = Crop.objects.filter(productor=request.user).select_related('finca')
    
    # Obtener cultivos cosechados que no tengan publicación activa
    crops = Crop.objects.filter(
        productor=request.user,
        estado='cosechado'
    ).exclude(
        publicaciones__estado='Activa'
    ).select_related('finca').order_by('-created_at')
    
    # Si no hay cultivos cosechados, mostrar todos los cultivos del usuario para que pueda ver qué tiene
    if not crops.exists():
        # Mostrar todos los cultivos del usuario para que pueda ver el estado
        crops = all_crops.order_by('-created_at')
        messages.info(request, 'No tienes cultivos cosechados disponibles para publicar. Aquí están todos tus cultivos:')
    
    context = {
        'crops': crops,
        'show_all_crops': not crops.filter(estado='cosechado').exclude(publicaciones__estado='Activa').exists()
    }
    return render(request, 'marketplace/select_crop_for_publication.html', context)

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


@login_required
def delete_publication_image(request, image_id):
    """Eliminar una imagen específica de una publicación"""
    from django.http import JsonResponse
    
    image = get_object_or_404(PublicationImage, pk=image_id)
    publication = image.publication
    
    # Verificar que el usuario sea el propietario
    if publication.cultivo.productor != request.user:
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
    
    # No permitir eliminar si es la única imagen
    if publication.images.count() <= 1:
        return JsonResponse({'success': False, 'error': 'Debe mantener al menos una imagen'}, status=400)
    
    # Si la imagen es principal y hay otras, hacer que la siguiente sea principal
    was_primary = image.is_primary
    image.delete()
    
    if was_primary:
        # Hacer que la primera imagen restante sea principal
        first_image = publication.images.first()
        if first_image:
            first_image.is_primary = True
            first_image.save()
    
    return JsonResponse({'success': True})


@login_required  
def set_primary_image(request, image_id):
    """Marcar una imagen como principal"""
    from django.http import JsonResponse
    
    image = get_object_or_404(PublicationImage, pk=image_id)
    publication = image.publication
    
    # Verificar que el usuario sea el propietario
    if publication.cultivo.productor != request.user:
        return JsonResponse({'success': False, 'error': 'No autorizado'}, status=403)
    
    # Quitar el flag de principal de todas las otras imágenes
    publication.images.update(is_primary=False)
    
    # Marcar esta como principal
    image.is_primary = True
    image.save()
    
    return JsonResponse({'success': True})