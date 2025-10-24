from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods
from django.contrib.auth import login, logout
from django.contrib.auth.views import LoginView
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.conf import settings
import random
import string
import time
from core.email_service import email_service
from core.firebase_phone_auth import firebase_phone_auth
from .forms import CustomUserCreationForm, BuyerRegistrationForm, UserEditForm, BuyerEditForm, ProducerProfileForm, BuyerProfileForm
from .forms_farm import ProducerRegistrationForm, ProducerProfileEditForm
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import ProducerProfile, BuyerProfile, User
from inventory.models import Crop
from django.urls import reverse_lazy, reverse
import logging

# Configurar logger
logger = logging.getLogger(__name__)
from marketplace.models import Publication
from marketplace.forms import PublicationForm
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from sales.models import Order
from core.models import Notification
from core.forms import FarmForm

# Create your views here.

def firebase_debug_view(request):
    return render(request, 'firebase_debug.html')

def google_auth_callback(request):
    """Callback para Google OAuth que procesa el login directamente"""
    code = request.GET.get('code')
    state = request.GET.get('state')
    error = request.GET.get('error')
    
    if error:
        # Si hay error, redirigir al login con mensaje de error
        return redirect(f'/accounts/login/?error={error}')
    
    if code and state:
        # Procesar el login directamente aquí
        try:
            # Intercambiar código por token
            import requests
            import json
            
            from django.conf import settings
            client_id = settings.GOOGLE_CLIENT_ID
            client_secret = settings.GOOGLE_CLIENT_SECRET
            redirect_uri = request.build_absolute_uri('/auth/google-callback/')
            
            token_url = 'https://oauth2.googleapis.com/token'
            token_data = {
                'client_id': client_id,
                'client_secret': client_secret,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri
            }
            
            response = requests.post(token_url, data=token_data)
            token_response = response.json()
            
            if 'access_token' in token_response:
                # Obtener información del usuario
                user_info_url = 'https://www.googleapis.com/oauth2/v2/userinfo'
                headers = {'Authorization': f'Bearer {token_response["access_token"]}'}
                user_response = requests.get(user_info_url, headers=headers)
                user_info = user_response.json()
                
                # Verificar si el usuario ya existe
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                try:
                    user = User.objects.get(email=user_info['email'])
                    # Usuario existe, hacer login
                    from django.contrib.auth import login
                    login(request, user)
                    return redirect('/')  # Redirigir al dashboard
                    
                except User.DoesNotExist:
                    # Usuario no existe, redirigir a completar registro
                    # Guardar datos de Google en la sesión
                    import time
                    request.session['google_user_data'] = {
                        'email': user_info['email'],
                        'first_name': user_info.get('given_name', ''),
                        'last_name': user_info.get('family_name', ''),
                        'photo_url': user_info.get('picture', ''),
                        'username_suggestion': user_info['email'].split('@')[0],  # Parte antes del @
                        'timestamp': time.time()  # Timestamp para expiración
                    }
                    
                    return redirect('/accounts/register/?from=google')  # Completar registro
            else:
                return redirect('/accounts/login/?error=token_error')
                
        except Exception as e:
            return redirect(f'/accounts/login/?error=processing_error')
    else:
        # Si no hay código, redirigir al login normal
        return redirect('/accounts/login/')

def register(request):
    """Registro para compradores (sin campos de finca)"""
    # Verificar si hay datos de Google en la sesión
    google_data = request.session.get('google_user_data', {})
    came_from_google = request.GET.get('from') == 'google'
    
    # Limpiar datos de Google si han pasado más de 10 minutos
    if google_data and 'timestamp' in google_data:
        import time
        if time.time() - google_data['timestamp'] > 600:  # 10 minutos
            if 'google_user_data' in request.session:
                del request.session['google_user_data']
            google_data = {}
    
    # Si no venimos del callback de Google, limpiar cualquier dato residual
    if not came_from_google and google_data:
        if 'google_user_data' in request.session:
            del request.session['google_user_data']
        google_data = {}

    # Si no hay datos de Google, limpiar cualquier dato residual de seguridad
    if not google_data:
        if 'google_user_data' in request.session:
            del request.session['google_user_data']
    
    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST, is_google_signup=bool(google_data))
        if form.is_valid():
            user = form.save()  # El formulario ya maneja la creación del perfil
            
            # Limpiar datos de Google de la sesión
            if 'google_user_data' in request.session:
                del request.session['google_user_data']
            
            login(request, user)
            messages.success(request, f'¡Bienvenido a AgroConnect, {user.first_name}!')
            return redirect('index')
    else:
        # Pre-llenar formulario con datos de Google solo si existen
        initial_data = {}
        if google_data:
            initial_data = {
                'email': google_data.get('email', ''),
                'first_name': google_data.get('first_name', ''),
                'last_name': google_data.get('last_name', ''),
                'username': google_data.get('username_suggestion', ''),
            }
        form = BuyerRegistrationForm(initial=initial_data, is_google_signup=bool(google_data))
    
    context = {
        'form': form,
        'google_data': google_data,
        'is_google_signup': bool(google_data),
        'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
        'GOOGLE_CLIENT_SECRET': settings.GOOGLE_CLIENT_SECRET,
        'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
        'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
        'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
        'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
        'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
        'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
    }
    
    return render(request, 'accounts/register.html', context)

@csrf_exempt
def clear_google_data(request):
    """Endpoint para limpiar datos de Google de la sesión"""
    if request.method == 'POST':
        if 'google_user_data' in request.session:
            del request.session['google_user_data']
            print("🧹 Datos de Google limpiados de la sesión")
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def register_producer(request):
    """Registro específico para productores con finca inicial"""
    # Obtener datos de Google si existen
    google_data = request.session.get('google_user_data', {})
    
    if request.method == 'POST':
        form = ProducerRegistrationForm(request.POST, is_google_signup=bool(google_data))
        if form.is_valid():
            user = form.save()
            
            # Crear BuyerProfile también (pueden comprar)
            BuyerProfile.objects.create(
                user=user,
                departamento=form.cleaned_data['finca_departamento'],
                ciudad=form.cleaned_data['finca_ciudad']
            )
            
            # Limpiar datos de Google de la sesión
            if 'google_user_data' in request.session:
                del request.session['google_user_data']
            
            login(request, user)
            messages.success(request, '¡Registro exitoso! Tu cuenta de productor y finca han sido creadas.')
            return redirect('core:farm_list')
    else:
        # Pre-llenar formulario con datos de Google
        initial_data = {}
        if google_data:
            initial_data = {
                'email': google_data.get('email', ''),
                'first_name': google_data.get('first_name', ''),
                'last_name': google_data.get('last_name', ''),
                'username': google_data.get('username_suggestion', ''),
            }
        form = ProducerRegistrationForm(initial=initial_data, is_google_signup=bool(google_data))
    
    context = {
        'form': form,
        'google_data': google_data,
        'is_google_signup': bool(google_data)
    }
    
    return render(request, 'accounts/register_producer.html', context)

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Agregar variables de Firebase y Google OAuth
        context.update({
            'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
            'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
            'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
            'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
            'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
            'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
            'GOOGLE_CLIENT_ID': settings.GOOGLE_CLIENT_ID,
            'GOOGLE_CLIENT_SECRET': settings.GOOGLE_CLIENT_SECRET,
        })
        return context

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
            # Usar formulario completo para productores
            try:
                producer_profile = request.user.producer_profile
                form = ProducerProfileEditForm(request.POST, request.FILES, instance=producer_profile, user=request.user)
            except AttributeError:
                # Si no tiene producer_profile, crear uno
                producer_profile = ProducerProfile.objects.create(user=request.user)
                form = ProducerProfileEditForm(request.POST, request.FILES, instance=producer_profile, user=request.user)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                return redirect('profile')
        else:
            # Usar formulario completo para compradores
            form = BuyerEditForm(request.POST, request.FILES, instance=request.user)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                return redirect('profile')
    else:
        if request.user.role == 'Productor':
            try:
                producer_profile = request.user.producer_profile
                form = ProducerProfileEditForm(instance=producer_profile, user=request.user)
            except AttributeError:
                # Si no tiene producer_profile, crear uno
                producer_profile = ProducerProfile.objects.create(user=request.user)
                form = ProducerProfileEditForm(instance=producer_profile, user=request.user)
        else:
            form = BuyerEditForm(instance=request.user)

    context = {
        'form': form,
    }
    return render(request, 'accounts/profile_edit.html', context)

def is_staff(user):
    return user.is_staff


@user_passes_test(is_staff)
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
                    'direccion': '',  # Campo no disponible en User
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
    
    if request.method == 'POST':
        print("Processing POST request...")
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
    print("Creating FarmForm...")
    farm_form = FarmForm()
    print("FarmForm created successfully")
    print(f"Departamento choices: {len(farm_form.fields['departamento'].choices)}")
    
    context = {
        'title': 'Convertirse en Vendedor',
        'user': request.user,
        'farm_form': farm_form,
    }
    print("Rendering template...")
    return render(request, 'accounts/become_seller.html', context)


# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('password_reset_done')
    form_class = PasswordResetForm

    def form_valid(self, form):
        # Obtener el email del formulario
        email = form.cleaned_data['email']
        
        # Buscar el usuario por email
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            
            # Verificar que el usuario tenga teléfono
            if not user.telefono:
                messages.error(self.request, 'Tu cuenta no tiene un número de teléfono registrado. Contacta soporte.')
                return self.form_invalid(form)
            
            # Generar código OTP de 6 dígitos
            otp_code = ''.join(random.choices(string.digits, k=6))
            
            # Guardar el código OTP en la sesión temporalmente (5 minutos)
            self.request.session['password_reset_otp'] = {
                'code': otp_code,
                'user_id': user.id,
                'email': email,
                'phone': user.telefono,
                'timestamp': time.time()
            }
            
            # Preparar datos para Firebase Phone Auth
            phone_auth_data = firebase_phone_auth.create_phone_auth_data(user.telefono, otp_code)
            
            # Guardar datos adicionales en la sesión para el frontend
            self.request.session['firebase_phone_auth'] = phone_auth_data
            
            messages.success(self.request, f'Código de verificación enviado a {user.telefono}')
            
            # Redirigir a la página de verificación de código
            return redirect('verify_phone_code')
            
        except User.DoesNotExist:
            messages.error(self.request, 'No existe una cuenta con ese correo electrónico.')
            return self.form_invalid(form)


class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'accounts/password_reset_done.html'


def password_reset_email(request):
    """Vista para recuperar contraseña por email usando Resend"""
    logger.info(f"=== INICIO ENVÍO EMAIL ===")
    logger.info(f"Método: {request.method}")
    
    if request.method == 'POST':
        email = request.POST.get('email')
        
        # Buscar el usuario por email
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
            
            # Generar código de recuperación de 6 dígitos
            import random
            recovery_code = str(random.randint(100000, 999999))
            
            # Calcular fecha de expiración (10 minutos)
            from django.utils import timezone
            from datetime import timedelta
            expires_at = timezone.now() + timedelta(minutes=10)
            
            # Crear registro del código de recuperación
            from .models import PasswordResetCode
            reset_code = PasswordResetCode.objects.create(
                user=user,
                code=recovery_code,
                email=email,
                expires_at=expires_at
            )
            
            # Debug: Log para verificar que el código se creó
            logger.info(f"DEBUG: Código creado - ID: {reset_code.id}, Código: {recovery_code}, Email: {email}, Expira: {expires_at}")
            
            # Crear URL de reset (opcional, para el botón del email)
            reset_url = request.build_absolute_uri(
                reverse('password_reset_confirm', kwargs={'uidb64': 'dummy', 'token': 'dummy'})
            )
            
            # Enviar correo con Resend
            success, message = email_service.send_password_reset_email(
                user.email, 
                reset_url, 
                user.get_full_name() or user.username,
                recovery_code
            )
            
            if success:
                messages.success(request, f'Se ha enviado un código de recuperación a {email}. El código expira en 10 minutos.')
                return redirect('password_reset_code_verification', email=email)
            else:
                messages.error(request, f'Error enviando correo: {message}')
                
        except User.DoesNotExist:
            messages.error(request, 'No existe una cuenta con ese correo electrónico.')
    
    return render(request, 'accounts/password_reset_email.html')


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'accounts/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')


def password_reset_code_verification(request, email):
    """Vista para verificar el código de recuperación enviado por email"""
    logger.info(f"=== INICIO VERIFICACIÓN CÓDIGO ===")
    logger.info(f"Email recibido: {email}")
    logger.info(f"Método: {request.method}")
    
    if request.method == 'POST':
        code = request.POST.get('code')
        
        try:
            # Buscar el código válido
            from .models import PasswordResetCode
            reset_code = PasswordResetCode.objects.filter(
                email=email,
                code=code,
                is_used=False
            ).first()
            
            # Debug: Log para verificar qué está pasando
            logger.info(f"DEBUG: Buscando código para email: {email}, código: {code}")
            logger.info(f"DEBUG: Código encontrado: {reset_code}")
            if reset_code:
                logger.info(f"DEBUG: Código válido: {reset_code.is_valid()}")
                logger.info(f"DEBUG: Código expirado: {reset_code.is_expired()}")
            
            if reset_code and reset_code.is_valid():
                # Marcar código como usado
                reset_code.is_used = True
                reset_code.save()
                
                # Redirigir a cambio de contraseña
                return redirect('password_reset_confirm', uidb64='code', token=code)
            else:
                messages.error(request, 'Código inválido o expirado. Por favor, solicita un nuevo código.')
                
        except Exception as e:
            logger.error(f"DEBUG: Error en verificación: {e}")
            messages.error(request, 'Error verificando el código. Inténtalo de nuevo.')
    
    return render(request, 'accounts/password_reset_code_verification.html', {'email': email})


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


def verify_phone_code(request):
    """Vista para verificar el código OTP enviado por SMS"""
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Obtener datos de la sesión
        otp_data = request.session.get('password_reset_otp', {})
        
        if not otp_data:
            messages.error(request, 'Sesión expirada. Por favor, solicita un nuevo código.')
            return redirect('password_reset')
        
        # Verificar que el código no haya expirado (5 minutos)
        if time.time() - otp_data.get('timestamp', 0) > 300:
            messages.error(request, 'El código ha expirado. Por favor, solicita uno nuevo.')
            del request.session['password_reset_otp']
            return redirect('password_reset')
        
        # Verificar el código OTP
        if verification_code != otp_data.get('code'):
            messages.error(request, 'Código de verificación incorrecto.')
            return render(request, 'accounts/verify_phone_code.html', {
                'phone_number': otp_data.get('phone', ''),
                'email': otp_data.get('email', ''),
                'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
                'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
                'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
                'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
                'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
                'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
            })
        
        # Verificar que las contraseñas coincidan
        if new_password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'accounts/verify_phone_code.html', {
                'phone_number': otp_data.get('phone', ''),
                'email': otp_data.get('email', ''),
                'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
                'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
                'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
                'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
                'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
                'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
            })
        
        if len(new_password) < 6:
            messages.error(request, 'La contraseña debe tener al menos 6 caracteres.')
            return render(request, 'accounts/verify_phone_code.html', {
                'phone_number': otp_data.get('phone', ''),
                'email': otp_data.get('email', ''),
                'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
                'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
                'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
                'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
                'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
                'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
            })
        
        # Cambiar la contraseña del usuario
        try:
            User = get_user_model()
            user = User.objects.get(id=otp_data['user_id'])
            user.set_password(new_password)
            user.save()
            
            # Limpiar la sesión
            del request.session['password_reset_otp']
            
            messages.success(request, 'Contraseña restablecida exitosamente. Ya puedes iniciar sesión.')
            return redirect('login')
            
        except User.DoesNotExist:
            messages.error(request, 'Usuario no encontrado.')
            return redirect('password_reset')
    
    # GET request - mostrar formulario
    otp_data = request.session.get('password_reset_otp', {})
    if not otp_data:
        messages.error(request, 'Sesión expirada. Por favor, solicita un nuevo código.')
        return redirect('password_reset')
    
    return render(request, 'accounts/verify_phone_code.html', {
        'phone_number': otp_data.get('phone', ''),
        'email': otp_data.get('email', ''),
        'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
        'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
        'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
        'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
        'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
        'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
    })
