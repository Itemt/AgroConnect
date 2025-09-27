from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Crop
from .forms import CropForm

# Create your views here.

@login_required
def crop_create_view(request):
    if request.user.role != 'Productor':
        return redirect('profile') # O a una página de error

    if request.method == 'POST':
        form = CropForm(request.POST)
        if form.is_valid():
            crop = form.save(commit=False)
            crop.producer = request.user
            crop.save()
            return redirect('profile')
    else:
        form = CropForm()
    
    return render(request, 'inventory/crop_form.html', {'form': form})

@login_required
def crop_update_view(request, pk):
    crop = get_object_or_404(Crop, pk=pk, producer=request.user)
    if request.method == 'POST':
        form = CropForm(request.POST, instance=crop)
        if form.is_valid():
            form.save()
            return redirect('profile')
    else:
        form = CropForm(instance=crop)

    return render(request, 'inventory/crop_form.html', {'form': form, 'crop': crop})

@login_required
def crop_delete_view(request, pk):
    crop = get_object_or_404(Crop, pk=pk, producer=request.user)
    if request.method == 'POST':
        crop.delete()
        return redirect('profile')
    
    return render(request, 'inventory/crop_confirm_delete.html', {'crop': crop})
