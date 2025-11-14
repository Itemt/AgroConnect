from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.views import LoginView, PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse_lazy, reverse
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
import random
import string
import time
import logging

from core.email_service import email_service
from core.firebase_phone_auth import firebase_phone_auth
from .forms import BuyerRegistrationForm, UserEditForm, BuyerEditForm, ProducerProfileForm, BuyerProfileForm, ProducerProfileEditForm
from .forms_farm import ProducerRegistrationForm
from .models import ProducerProfile, BuyerProfile, User
from inventory.models import Crop
from marketplace.models import Publication
from sales.models import Order
from core.models import Notification
from core.forms import FarmForm

# Configurar logger
logger = logging.getLogger(__name__)

# Create your views here.


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
            # Obtener photo_url de Google si existe
            google_photo_url = google_data.get('photo_url', '') if google_data else None
            user = form.save(google_photo_url=google_photo_url)  # El formulario ya maneja la creación del perfil
            
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
        # NOTA: GOOGLE_CLIENT_SECRET no se incluye por seguridad (solo debe usarse en backend)
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
        return JsonResponse({'success': True})
    return JsonResponse({'success': False})

def register_producer(request):
    """Registro específico para productores con finca inicial"""
    # Obtener datos de Google si existen
    google_data = request.session.get('google_user_data', {})
    
    if request.method == 'POST':
        form = ProducerRegistrationForm(request.POST, is_google_signup=bool(google_data))
        if form.is_valid():
            # Obtener photo_url de Google si existe
            google_photo_url = google_data.get('photo_url', '') if google_data else None
            user = form.save(google_photo_url=google_photo_url)
            
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
            # NOTA: GOOGLE_CLIENT_SECRET no se incluye por seguridad (solo debe usarse en backend)
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
    
    # Renderizar template apropiado según el rol
    if request.user.role == 'Productor':
        return render(request, 'accounts/profile_producer.html', context)
    else:
        return render(request, 'accounts/profile_buyer.html', context)

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
                return redirect('profile_edit')
        else:
            # Usar formulario completo para compradores
            form = BuyerEditForm(request.POST, request.FILES, instance=request.user)
            
            if form.is_valid():
                form.save()
                messages.success(request, 'Perfil actualizado exitosamente.')
                return redirect('profile_edit')
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
            # Use TailAdmin template for buyers
            return render(request, 'accounts/become_seller_tailadmin.html', context)
    
    # Crear formulario de finca para el primer paso
    farm_form = FarmForm()
    
    context = {
        'title': 'Convertirse en Vendedor',
        'user': request.user,
        'farm_form': farm_form,
    }
    # Use TailAdmin template for buyers
    return render(request, 'accounts/become_seller_tailadmin.html', context)


# Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'accounts/password_reset.html'
    email_template_name = 'accounts/password_reset_email_template.html'
    subject_template_name = 'accounts/password_reset_subject.txt'
    success_url = reverse_lazy('verify_phone_code')
    form_class = None  # Usaremos nuestro propio formulario
    
    def get_form_class(self):
        from .forms import PhonePasswordResetForm
        return PhonePasswordResetForm

    @staticmethod
    def _normalize_phone_variants(phone_number: str):
        """
        Devuelve el número normalizado (formato +57XXXXXXXXXX) y las variantes posibles
        que pueden existir en la base de datos (con/sin +, sin código de país, etc.)
        """
        if not phone_number:
            return '', []
        
        digits_only = ''.join(filter(str.isdigit, phone_number))
        normalized = firebase_phone_auth._clean_phone_number(phone_number)
        
        if not normalized and digits_only:
            if digits_only.startswith('3') and len(digits_only) == 10:
                normalized = f"+57{digits_only}"
            elif digits_only.startswith('57'):
                normalized = f"+{digits_only}"
            else:
                normalized = f"+{digits_only}"
        
        variants = []
        if normalized:
            variants.append(normalized)
            digits = normalized.replace('+', '')
            variants.append(digits)
            if digits.startswith('57') and len(digits) > 2:
                variants.append(digits[2:])
        else:
            variants.append(phone_number)
        
        # Variante sin espacios ni guiones del número original
        if digits_only:
            compact = f"+{digits_only}" if not digits_only.startswith('+') else digits_only
            if compact not in variants:
                variants.append(compact)
        
        # Eliminar duplicados preservando orden
        variants = [v for i, v in enumerate(variants) if v and v not in variants[:i]]
        return normalized or phone_number, variants

    def form_valid(self, form):
        # Obtener el teléfono del formulario
        telefono = form.cleaned_data['telefono']
        normalized_phone, phone_variants = self._normalize_phone_variants(telefono)
        
        # Buscar el usuario por teléfono
        User = get_user_model()
        user = User.objects.filter(telefono__in=phone_variants or [telefono]).first()
        
        # Ocultar parte del número para mostrar en el mensaje
        # Por ejemplo: +57 300 123 4567 -> +57 300 XXX XX67
        phone_display = normalized_phone or telefono
        if len(telefono) > 6:
            phone_display = telefono[:-4] + ' XXX XX' + telefono[-2:]
        
        try:
            if not user:
                raise User.DoesNotExist

            # Generar código OTP de 6 dígitos
            otp_code = ''.join(random.choices(string.digits, k=6))
            
            # Preparar datos para Firebase Phone Auth
            phone_auth_data = firebase_phone_auth.create_phone_auth_data(normalized_phone or user.telefono, otp_code)
            
            # Guardar datos en la sesión para el frontend
            self.request.session['firebase_phone_auth'] = phone_auth_data
            self.request.session['password_reset_otp'] = {
                'user_id': user.id,
                'phone': phone_auth_data['phone_number'],
                'email': user.email,
                'otp_code': otp_code,
                'timestamp': time.time()
            }
            
            messages.success(self.request, f'Se enviará un código de verificación al número registrado.')
            
        except User.DoesNotExist:
            # Guardar datos ficticios en la sesión para no revelar que el usuario no existe
            self.request.session['firebase_phone_auth'] = {
                'phone_number': normalized_phone or telefono,
                'invalid_user': True
            }
            self.request.session['password_reset_otp'] = {
                'user_id': None,
                'phone': normalized_phone or telefono,
                'email': '',
                'otp_code': '',
                'timestamp': time.time(),
                'invalid_user': True
            }
            
            # Mostrar el mismo mensaje (seguridad)
            messages.success(self.request, f'Se enviará un código de verificación al número registrado.')
        
        # Siempre redirigir a la página de verificación de código
        return redirect('verify_phone_code')


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
            
            # Log para verificar que el código se creó
            logger.info(f"Código creado - ID: {reset_code.id}, Email: {email}, Expira: {expires_at}")
            
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


def password_reset_confirm_with_code(request, uidb64, token):
    """Vista personalizada para establecer nueva contraseña usando código"""
    logger.info(f"=== INICIO CONFIRMACIÓN CONTRASEÑA ===")
    logger.info(f"uidb64: {uidb64}, token: {token}")
    
    if request.method == 'POST':
        new_password = request.POST.get('new_password1')
        confirm_password = request.POST.get('new_password2')
        
        logger.info(f"Nueva contraseña recibida: {bool(new_password)}")
        logger.info(f"Confirmar contraseña recibida: {bool(confirm_password)}")
        
        if new_password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden.')
            return render(request, 'accounts/password_reset_confirm.html')
        
        if len(new_password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'accounts/password_reset_confirm.html')
        
        # Buscar el código usado
        try:
            from .models import PasswordResetCode
            reset_code = PasswordResetCode.objects.filter(
                code=uidb64,
                is_used=True
            ).first()
            
            logger.info(f"Código encontrado: {reset_code}")
            
            if reset_code:
                # Cambiar la contraseña del usuario
                user = reset_code.user
                user.set_password(new_password)
                user.save()
                
                # Eliminar el código usado
                reset_code.delete()
                
                # Iniciar sesión automáticamente
                login(request, user)
                
                logger.info(f"Contraseña actualizada para usuario: {user.email}")
                messages.success(request, 'Contraseña actualizada exitosamente. Sesión iniciada.')
                return redirect('index')
            else:
                messages.error(request, 'Código de recuperación inválido o expirado.')
                
        except Exception as e:
            logger.error(f"Error actualizando contraseña: {e}")
            messages.error(request, 'Error actualizando la contraseña. Inténtalo de nuevo.')
    
    return render(request, 'accounts/password_reset_confirm.html')


class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'accounts/password_reset_complete.html'


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
            
            # Log para verificar qué está pasando
            logger.info(f"Buscando código para email: {email}")
            logger.info(f"Código encontrado: {reset_code}")
            if reset_code:
                logger.info(f"Código válido: {reset_code.is_valid()}")
                logger.info(f"Código expirado: {reset_code.is_expired()}")
            
            if reset_code and reset_code.is_valid():
                # Marcar código como usado
                reset_code.is_used = True
                reset_code.save()
                
                # Redirigir a cambio de contraseña
                return redirect('password_reset_confirm', uidb64='code', token=code)
            else:
                messages.error(request, 'Código inválido o expirado. Por favor, solicita un nuevo código.')
                
        except Exception as e:
            logger.error(f"Error en verificación: {e}")
            messages.error(request, 'Error verificando el código. Inténtalo de nuevo.')
    
    return render(request, 'accounts/password_reset_code_verification.html', {'email': email})


def send_otp_ajax(request):
    """Vista AJAX para enviar código OTP usando Firebase"""
    if request.method == 'POST':
        try:
            phone_number = request.POST.get('phone_number')
            if not phone_number:
                return JsonResponse({'success': False, 'message': 'Número de teléfono requerido'})
            
            # Limpiar y formatear número de teléfono
            clean_phone = firebase_phone_auth._clean_phone_number(phone_number)
            if not clean_phone:
                return JsonResponse({'success': False, 'message': 'Número de teléfono inválido'})
            
            # Guardar datos en la sesión para verificación posterior
            request.session['firebase_phone_auth'] = {
                'phone_number': clean_phone,
                'timestamp': time.time()
            }
            
            return JsonResponse({
                'success': True, 
                'message': 'Código OTP enviado correctamente',
                'phone_number': clean_phone
            })
            
        except Exception as e:
            logger.error(f"Error enviando OTP: {str(e)}")
            return JsonResponse({'success': False, 'message': 'Error enviando código OTP'})
    
    return JsonResponse({'success': False, 'message': 'Método no permitido'})




def verify_phone_code(request):
    """Vista para verificar el código OTP enviado por SMS usando Firebase"""
    if request.method == 'POST':
        otp_verified = request.POST.get('otp_verified') == 'true'
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Obtener datos de la sesión
        otp_data = request.session.get('password_reset_otp', {})
        firebase_data = request.session.get('firebase_phone_auth', {})
        
        if not otp_data or not firebase_data:
            messages.error(request, 'Sesión expirada. Por favor, solicita un nuevo código.')
            return redirect('password_reset')
        
        # Verificar si es un usuario inválido
        if otp_data.get('invalid_user') or firebase_data.get('invalid_user'):
            messages.error(request, 'El número de teléfono no está asociado a ninguna cuenta.')
            del request.session['password_reset_otp']
            del request.session['firebase_phone_auth']
            return redirect('password_reset')
        
        # Verificar que el código no haya expirado (5 minutos)
        if time.time() - otp_data.get('timestamp', 0) > 300:
            messages.error(request, 'El código ha expirado. Por favor, solicita uno nuevo.')
            del request.session['password_reset_otp']
            del request.session['firebase_phone_auth']
            return redirect('password_reset')
        
        # Verificar que el OTP haya sido verificado en el frontend
        if not otp_verified:
            messages.error(request, 'Por favor verifica el código OTP primero.')
            return render(request, 'accounts/verify_phone_code.html', {
                'phone_number': firebase_data.get('phone_number', ''),
                'email': otp_data.get('email', ''),
                'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
                'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
                'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
                'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
                'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
                'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
            })
        
        # Verificar que las contraseñas estén presentes
        if not new_password or not confirm_password:
            messages.error(request, 'Por favor completa todos los campos de contraseña.')
            return render(request, 'accounts/verify_phone_code.html', {
                'phone_number': firebase_data.get('phone_number', ''),
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
                'phone_number': firebase_data.get('phone_number', ''),
                'email': otp_data.get('email', ''),
                'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
                'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
                'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
                'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
                'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
                'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
            })
        
        if len(new_password) < 8:
            messages.error(request, 'La contraseña debe tener al menos 8 caracteres.')
            return render(request, 'accounts/verify_phone_code.html', {
                'phone_number': firebase_data.get('phone_number', ''),
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
            logger.info(f"Cambiando contraseña para usuario ID: {user.id}, Email: {user.email}")
            user.set_password(new_password)
            user.save()
            logger.info(f"Contraseña actualizada exitosamente para usuario: {user.email}")
            
            # Limpiar la sesión
            del request.session['password_reset_otp']
            del request.session['firebase_phone_auth']
            
            # Iniciar sesión automáticamente
            login(request, user)
            logger.info(f"Sesión iniciada para usuario: {user.email}")
            
            messages.success(request, 'Contraseña restablecida exitosamente. Sesión iniciada.')
            return redirect('index')
            
        except User.DoesNotExist:
            logger.error(f"Usuario no encontrado con ID: {otp_data.get('user_id')}")
            messages.error(request, 'Usuario no encontrado.')
            return redirect('password_reset')
        except Exception as e:
            logger.error(f"Error cambiando contraseña: {e}")
            messages.error(request, f'Error al cambiar la contraseña: {str(e)}')
            return render(request, 'accounts/verify_phone_code.html', {
                'phone_number': firebase_data.get('phone_number', ''),
                'email': otp_data.get('email', ''),
                'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
                'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
                'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
                'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
                'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
                'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
            })
    
    # GET request - mostrar formulario
    otp_data = request.session.get('password_reset_otp', {})
    firebase_data = request.session.get('firebase_phone_auth', {})
    
    if not otp_data or not firebase_data:
        messages.error(request, 'Sesión expirada. Por favor, solicita un nuevo código.')
        return redirect('password_reset')
    
    return render(request, 'accounts/verify_phone_code.html', {
        'phone_number': firebase_data.get('phone_number', ''),
        'email': otp_data.get('email', ''),
        'FIREBASE_API_KEY': settings.FIREBASE_API_KEY,
        'FIREBASE_AUTH_DOMAIN': settings.FIREBASE_AUTH_DOMAIN,
        'FIREBASE_PROJECT_ID': settings.FIREBASE_PROJECT_ID,
        'FIREBASE_STORAGE_BUCKET': settings.FIREBASE_STORAGE_BUCKET,
        'FIREBASE_MESSAGING_SENDER_ID': settings.FIREBASE_MESSAGING_SENDER_ID,
        'FIREBASE_APP_ID': settings.FIREBASE_APP_ID,
    })


