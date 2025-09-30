from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, UserEditForm, ProducerProfileForm, BuyerProfileForm, AdminUserEditForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ProducerProfile, BuyerProfile, User
from inventory.models import Crop
from django.urls import reverse_lazy, reverse
from marketplace.models import Publication
from marketplace.forms import PublicationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from sales.models import Order

# Create your views here.

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = form.cleaned_data['role']
            user.save()

            departamento = form.cleaned_data['departamento']
            ciudad = form.cleaned_data['ciudad']

            if user.role == 'Productor':
                ProducerProfile.objects.create(
                    user=user,
                    departamento=departamento,
                    ciudad=ciudad
                )
            elif user.role == 'Comprador':
                BuyerProfile.objects.create(
                    user=user,
                    departamento=departamento,
                    ciudad=ciudad
                )

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
        user_form = UserEditForm(request.POST, request.FILES, instance=request.user)
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

@user_passes_test(is_staff)
def admin_publication_list(request):
    publications = Publication.objects.all().select_related(
        'cultivo__productor', 
        'cultivo__producto'
    ).order_by('-created_at')
    return render(request, 'accounts/admin_publication_list.html', {'publications': publications})

@user_passes_test(is_staff)
def admin_publication_edit(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        form = PublicationForm(request.POST, instance=publication)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publicación actualizada exitosamente.')
            return redirect('admin_publication_list')
    else:
        form = PublicationForm(instance=publication)
    
    context = {
        'form': form,
        'publication': publication,
        'title': 'Editar Publicación (Admin)'
    }
    return render(request, 'marketplace/publication_form.html', context)

@user_passes_test(is_staff)
def admin_publication_delete(request, pk):
    publication = get_object_or_404(Publication, pk=pk)
    if request.method == 'POST':
        publication.delete() 
        messages.success(request, 'Publicación eliminada exitosamente.')
        return redirect('admin_publication_list')
    
    context = {
        'publication': publication
    }
    return render(request, 'marketplace/publication_confirm_delete.html', context)

@user_passes_test(is_staff)
def admin_user_list(request):
    users = User.objects.all().order_by('username')
    return render(request, 'accounts/admin_user_list.html', {'users': users})

@user_passes_test(is_staff)
def admin_user_edit(request, pk):
    user_to_edit = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user_to_edit)
        if form.is_valid():
            form.save()
            messages.success(request, f'Usuario {user_to_edit.username} actualizado exitosamente.')
            return redirect('admin_user_list')
    else:
        form = AdminUserEditForm(instance=user_to_edit)
    
    context = {
        'form': form,
        'user_to_edit': user_to_edit,
        'title': 'Editar Usuario'
    }
    return render(request, 'accounts/admin_user_form.html', context)

@user_passes_test(is_staff)
def admin_user_delete(request, pk):
    user_to_delete = get_object_or_404(User, pk=pk)
    if request.method == 'POST':
        # No permitir que un admin se borre a sí mismo
        if request.user.pk == user_to_delete.pk:
            messages.error(request, 'No puedes eliminar tu propia cuenta de administrador.')
            return redirect('admin_user_list')
        
        user_to_delete.delete()
        messages.success(request, f'Usuario {user_to_delete.username} eliminado exitosamente.')
        return redirect('admin_user_list')
    
    context = {
        'user_to_delete': user_to_delete
    }
    return render(request, 'accounts/admin_user_confirm_delete.html', context)

@user_passes_test(is_staff)
def admin_order_list(request):
    orders = Order.objects.all().select_related(
        'publicacion__cultivo__producto',
        'comprador',
        'publicacion__cultivo__productor'
    ).order_by('-created_at')
    return render(request, 'accounts/admin_order_list.html', {'orders': orders})

@user_passes_test(is_staff)
def admin_order_detail(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    # Para un admin, no verificamos si es comprador o vendedor.
    # Podemos añadir acciones específicas de admin si es necesario en el futuro.
    
    context = {
        'order': order,
        'user_role': 'admin' # Pasamos un rol especial para la plantilla
    }
    return render(request, 'sales/order_detail.html', context)
