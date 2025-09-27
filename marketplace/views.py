from django.shortcuts import render, get_object_or_404, redirect
from .models import Publication
from django.contrib.auth.decorators import login_required
from inventory.models import Crop
from .forms import PublicationForm

# Create your views here.

def marketplace_view(request):
    publications = Publication.objects.filter(status='disponible').order_by('-created_at')
    context = {
        'publications': publications
    }
    return render(request, 'marketplace/marketplace.html', context)

def publication_detail_view(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    context = {
        'publication': publication
    }
    return render(request, 'marketplace/publication_detail.html', context)

@login_required
def publication_create_view(request, crop_id):
    crop = get_object_or_404(Crop, pk=crop_id, producer=request.user)
    
    if hasattr(crop, 'publication'):
        # Si ya existe una publicación, redirigir a la edición (funcionalidad futura)
        return redirect('profile')

    if request.method == 'POST':
        form = PublicationForm(request.POST)
        if form.is_valid():
            publication = form.save(commit=False)
            publication.crop = crop
            publication.save()
            return redirect('profile')
    else:
        # Pre-llenar el formulario con la cantidad del cultivo
        form = PublicationForm(initial={'available_quantity': crop.estimated_quantity})

    context = {
        'form': form,
        'crop': crop
    }
    return render(request, 'marketplace/publication_form.html', context)
