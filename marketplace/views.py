from django.shortcuts import render, get_object_or_404
from .models import Publication

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
