from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, UserEditForm, ProducerProfileForm, BuyerProfileForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ProducerProfile, BuyerProfile
from inventory.models import Crop
from django.urls import reverse_lazy

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('index')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_success_url(self):
        user = self.request.user
        if user.is_authenticated:
            if user.is_staff:
                return reverse_lazy('admin_dashboard')
            
            if user.role == 'Productor':
                return reverse_lazy('producer_dashboard')
            elif user.role == 'Comprador':
                return reverse_lazy('buyer_dashboard')
        
        return reverse_lazy('index')

def custom_logout(request):
    logout(request)
    return redirect('index')

@login_required
def profile_view(request):
    crops = None
    if request.user.role == 'Productor':
        # La relación inversa desde User a Crop se llama 'cultivos'
        crops = request.user.cultivos.all().order_by('-created_at')
    
    context = {
        'crops': crops
    }
    return render(request, 'accounts/profile.html', context)

@login_required
def profile_edit_view(request):
    ProfileForm = None
    if request.user.role == 'Productor':
        ProfileForm = ProducerProfileForm
        # Asegurarse de que exista un perfil para el productor
        profile, created = ProducerProfile.objects.get_or_create(user=request.user)
    elif request.user.role == 'Comprador':
        ProfileForm = BuyerProfileForm
        # Asegurarse de que exista un perfil para el comprador
        profile, created = BuyerProfile.objects.get_or_create(user=request.user)
    else:
        profile = None

    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=profile) if profile else None
        
        if user_form.is_valid() and (not profile_form or profile_form.is_valid()):
            user_form.save()
            if profile_form:
                profile_form.save()
            return redirect('profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileForm(instance=profile) if profile else None

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'accounts/profile_edit.html', context)

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def admin_dashboard(request):
    return render(request, 'accounts/admin_dashboard.html')
