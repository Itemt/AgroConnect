from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from .forms import CustomUserCreationForm, BuyerRegistrationForm, UserEditForm, BuyerEditForm, ProducerProfileForm, BuyerProfileForm
from .forms_farm import ProducerRegistrationForm, ProducerProfileEditForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ProducerProfile, BuyerProfile, User
from inventory.models import Crop
from django.urls import reverse_lazy, reverse
from marketplace.models import Publication
from marketplace.forms import PublicationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from sales.models import Order
from core.models import Notification
from core.forms import FarmForm

# Create your views here.

def register(request):
    """Registro para compradores (sin campos de finca)"""
    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()  # El formulario ya maneja la creación del perfil
            login(request, user)
            messages.success(request, f'¡Bienvenido a AgroConnect, {user.first_name}!')
            return redirect('index')
    else:
        form = BuyerRegistrationForm()
    
    return render(request, 'accounts/register_buyer.html', {'form': form})

def register_producer(request):
    """Registro específico para productores con finca inicial"""
    if request.method == 'POST':
        form = ProducerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Crear BuyerProfile también (pueden comprar)
            BuyerProfile.objects.create(
                user=user,
                departamento=form.cleaned_data['finca_departamento'],
                ciudad=form.cleaned_data['finca_ciudad']
            )
            
            login(request, user)
            messages.success(request, '¡Registro exitoso! Tu cuenta de productor y finca han sido creadas.')
            return redirect('core:farm_list')
    else:
        form = ProducerRegistrationForm()
    
    return render(request, 'accounts/register_producer.html', {'form': form})

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
    if request.method == 'POST':
        if request.user.role == 'Productor':
            # Usar formulario extendido para productores
            try:
                producer_profile = request.user.producerprofile
                form = ProducerProfileEditForm(request.POST, instance=producer_profile, user=request.user)
            except ProducerProfile.DoesNotExist:
                form = ProducerProfileEditForm(request.POST, user=request.user)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                return redirect('profile')
        else:
            # Usar formulario específico para compradores (sin campos de finca)
            form = BuyerEditForm(request.POST, request.FILES, instance=request.user)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                return redirect('profile')
    else:
        if request.user.role == 'Productor':
            try:
                producer_profile = request.user.producerprofile
                form = ProducerProfileEditForm(instance=producer_profile, user=request.user)
            except ProducerProfile.DoesNotExist:
                form = ProducerProfileEditForm(user=request.user)
        else:
            form = BuyerEditForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'accounts/profile_edit.html', context)

def is_staff(user):
    return user.is_staff

@user_passes_test(is_staff)
def admin_dashboard(request):
    from sales.models import Order
    from marketplace.models import Publication
    from inventory.models import Crop
    
    # Estadísticas
    total_users = User.objects.count()
    total_crops = Crop.objects.count()
    total_publications = Publication.objects.count()
    total_orders = Order.objects.count()
    
    # Usuarios recientes
    recent_users = User.objects.order_by('-date_joined')[:5]
    
    context = {
        'total_users': total_users,
        'total_crops': total_crops,
        'total_publications': total_publications,
        'total_orders': total_orders,
        'recent_users': recent_users,
        'recent_notifications': Notification.objects.filter(recipient=request.user).order_by('-created_at')[:20],
    }
    return render(request, 'accounts/admin_dashboard.html', context)

@user_passes_test(is_staff)
def admin_publication_list(request):
    publications = Publication.objects.all().select_related(
        'cultivo__productor', 
        'cultivo'
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

@user_passes_test(is_staff)
def admin_order_edit(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method == 'POST':
        estado = request.POST.get('estado')
        if estado:
            order.estado = estado
            order.save()
            messages.success(request, f'Estado de la orden #{order.id} actualizado exitosamente.')
            return redirect('admin_order_list')
    
    # Obtener las opciones de estado
    estado_choices = Order.ESTADO_CHOICES
    
    context = {
        'order': order,
        'estado_choices': estado_choices,
    }
    return render(request, 'accounts/admin_order_edit.html', context)

@user_passes_test(is_staff)
def admin_order_delete(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    
    if request.method == 'POST':
        order_number = order.id
        order.delete()
        messages.success(request, f'Orden #{order_number} eliminada exitosamente.')
        return redirect('admin_order_list')
    
    context = {
        'order': order,
    }
    return render(request, 'accounts/admin_order_confirm_delete.html', context)

# ===== CRUD COMPLETO DE USUARIOS =====
@user_passes_test(is_staff)
def admin_user_create(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        role = request.POST.get('role')
        cedula = request.POST.get('cedula')
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=role,
            cedula=cedula
        )
        messages.success(request, f'Usuario {username} creado exitosamente.')
        return redirect('admin_user_list')
    
    return render(request, 'accounts/admin_user_create.html')

# ===== CRUD COMPLETO DE CULTIVOS =====
@user_passes_test(is_staff)
def admin_crop_list(request):
    from inventory.models import Crop
    crops = Crop.objects.all().select_related('productor').order_by('-created_at')
    return render(request, 'accounts/admin_crop_list.html', {'crops': crops})

@user_passes_test(is_staff)
def admin_crop_create(request):
    from inventory.forms import CropForm
    if request.method == 'POST':
        form = CropForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cultivo creado exitosamente.')
            return redirect('admin_crop_list')
    else:
        form = CropForm()
    
    context = {
        'form': form,
        'title': 'Crear Cultivo (Admin)'
    }
    return render(request, 'accounts/admin_crop_form.html', context)

@user_passes_test(is_staff)
def admin_crop_edit(request, pk):
    from inventory.models import Crop
    from inventory.forms import CropForm
    crop = get_object_or_404(Crop, pk=pk)
    
    if request.method == 'POST':
        form = CropForm(request.POST, instance=crop)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cultivo actualizado exitosamente.')
            return redirect('admin_crop_list')
    else:
        form = CropForm(instance=crop)
    
    context = {
        'form': form,
        'crop': crop,
        'title': 'Editar Cultivo (Admin)'
    }
    return render(request, 'accounts/admin_crop_form.html', context)

@user_passes_test(is_staff)
def admin_crop_delete(request, pk):
    from inventory.models import Crop
    crop = get_object_or_404(Crop, pk=pk)
    
    if request.method == 'POST':
        crop_name = crop.nombre
        crop.delete()
        messages.success(request, f'Cultivo "{crop_name}" eliminado exitosamente.')
        return redirect('admin_crop_list')
    
    context = {
        'crop': crop
    }
    return render(request, 'accounts/admin_crop_confirm_delete.html', context)

# ===== CREATE DE PUBLICACIONES =====
@user_passes_test(is_staff)
def admin_publication_create(request):
    from marketplace.forms import PublicationForm
    if request.method == 'POST':
        form = PublicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publicación creada exitosamente.')
            return redirect('admin_publication_list')
    else:
        form = PublicationForm()
    
    context = {
        'form': form,
        'title': 'Crear Publicación (Admin)'
    }
    return render(request, 'marketplace/publication_form.html', context)

@login_required
def become_seller(request):
    """Vista para que un comprador se convierta en vendedor"""
    if request.user.role != 'Comprador':
        messages.error(request, 'Esta opción solo está disponible para compradores.')
        return redirect('index')
    
    if request.method == 'POST':
        # Procesar formulario de finca
        farm_form = FarmForm(request.POST)
        
        if farm_form.is_valid():
            # Crear perfil de productor
            producer_profile, created = ProducerProfile.objects.get_or_create(
                user=request.user,
                defaults={
                    'telefono': request.user.telefono,
                    'direccion': request.user.direccion,
                    'ciudad': request.user.ciudad,
                    'departamento': request.user.departamento,
                }
            )
            
            # Cambiar rol del usuario
            request.user.role = 'Productor'
            request.user.save()
            
            # Crear la finca
            finca = farm_form.save(commit=False)
            finca.propietario = request.user
            finca.save()
            
            messages.success(request, f'¡Felicidades! Ahora eres un vendedor. Tu finca "{finca.nombre}" ha sido creada exitosamente.')
            return redirect('core:farm_detail', pk=finca.pk)
        else:
            # Si hay errores, mostrar el formulario con errores
            context = {
                'title': 'Convertirse en Vendedor',
                'user': request.user,
                'farm_form': farm_form,
            }
            return render(request, 'accounts/become_seller.html', context)
    
    # Crear formulario de finca para el primer paso
    farm_form = FarmForm()
    
    context = {
        'title': 'Convertirse en Vendedor',
        'user': request.user,
        'farm_form': farm_form,
    }
    return render(request, 'accounts/become_seller.html', context)
