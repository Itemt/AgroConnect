"""
Vistas para autenticación con Firebase
Maneja Google Sign-In y SMS OTP para recuperación de contraseñas
"""

import json
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import User, BuyerProfile
from .firebase_service import FirebaseAuthService, get_firebase_auth
import requests


@csrf_exempt
@require_http_methods(["POST"])
def google_signin(request):
    """
    Vista para manejar el inicio de sesión con Google
    Recibe el token de ID de Google y crea/autentica al usuario
    """
    try:
        data = json.loads(request.body)
        id_token = data.get('idToken')
        
        if not id_token:
            return JsonResponse({
                'success': False,
                'error': 'Token no proporcionado'
            }, status=400)
        
        # Verificar el token con Firebase
        user_info = FirebaseAuthService.verify_google_token(id_token)
        
        if not user_info:
            return JsonResponse({
                'success': False,
                'error': 'Token inválido'
            }, status=400)
        
        # Buscar o crear el usuario en Django
        email = user_info.get('email')
        name = user_info.get('name', '')
        picture = user_info.get('picture', '')
        
        # Separar nombre y apellido
        name_parts = name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        # Buscar usuario existente por email
        try:
            user = User.objects.get(email=email)
            # Usuario existente, solo iniciar sesión
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Inicio de sesión exitoso',
                'redirect_url': '/accounts/profile/' if user.role else '/accounts/complete-profile/'
            })
            
        except User.DoesNotExist:
            # Crear nuevo usuario
            # Generar username único basado en el email
            username = email.split('@')[0]
            base_username = username
            counter = 1
            
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1
            
            # Crear usuario sin contraseña (se autentica solo con Google)
            user = User.objects.create(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                role='Comprador',  # Por defecto es comprador
            )
            user.set_unusable_password()  # No puede usar contraseña tradicional
            user.save()
            
            # Crear perfil de comprador
            BuyerProfile.objects.create(user=user)
            
            # Iniciar sesión
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
            
            return JsonResponse({
                'success': True,
                'message': 'Registro exitoso con Google',
                'redirect_url': '/accounts/complete-profile/',
                'new_user': True
            })
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos inválidos'
        }, status=400)
    except Exception as e:
        print(f"Error en google_signin: {e}")
        return JsonResponse({
            'success': False,
            'error': f'Error al procesar la solicitud: {str(e)}'
        }, status=500)


@login_required
def complete_profile(request):
    """
    Vista para completar el perfil después del registro con Google
    """
    if request.user.telefono and request.user.ciudad and request.user.departamento:
        # Perfil ya completado
        return redirect('profile')
    
    if request.method == 'POST':
        telefono = request.POST.get('telefono')
        cedula = request.POST.get('cedula')
        departamento = request.POST.get('departamento')
        ciudad = request.POST.get('ciudad')
        
        # Actualizar usuario
        request.user.telefono = telefono
        request.user.cedula = cedula
        request.user.departamento = departamento
        request.user.ciudad = ciudad
        request.user.save()
        
        # Actualizar perfil de comprador
        if hasattr(request.user, 'buyer_profile'):
            request.user.buyer_profile.departamento = departamento
            request.user.buyer_profile.ciudad = ciudad
            request.user.buyer_profile.save()
        
        messages.success(request, 'Perfil completado exitosamente')
        return redirect('profile')
    
    context = {
        'user': request.user
    }
    return render(request, 'accounts/complete_profile.html', context)


def password_reset_phone(request):
    """
    Vista para solicitar recuperación de contraseña por SMS
    """
    if request.method == 'POST':
        phone_number = request.POST.get('phone_number')
        
        # Validar formato de número de teléfono (debe incluir código de país)
        if not phone_number.startswith('+'):
            messages.error(request, 'El número de teléfono debe incluir el código de país (ej: +573001234567)')
            return render(request, 'accounts/password_reset_phone.html')
        
        # Buscar usuario por teléfono
        try:
            user = User.objects.get(telefono=phone_number)
        except User.DoesNotExist:
            messages.error(request, 'No existe un usuario registrado con ese número de teléfono')
            return render(request, 'accounts/password_reset_phone.html')
        
        # Enviar código de verificación por SMS
        result = FirebaseAuthService.send_password_reset_sms(phone_number)
        
        if result.get('success'):
            # Guardar el teléfono en la sesión para verificación posterior
            request.session['password_reset_phone'] = phone_number
            messages.success(request, 'Se ha enviado un código de verificación a tu teléfono')
            return redirect('verify_phone_code')
        else:
            messages.error(request, f'Error al enviar SMS: {result.get("error")}')
            return render(request, 'accounts/password_reset_phone.html')
    
    return render(request, 'accounts/password_reset_phone.html')


def verify_phone_code(request):
    """
    Vista para verificar el código SMS y restablecer la contraseña
    """
    phone_number = request.session.get('password_reset_phone')
    
    if not phone_number:
        messages.error(request, 'Sesión expirada. Por favor, solicita un nuevo código.')
        return redirect('password_reset_phone')
    
    if request.method == 'POST':
        code = request.POST.get('verification_code')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        
        # Validar que las contraseñas coincidan
        if new_password != confirm_password:
            messages.error(request, 'Las contraseñas no coinciden')
            return render(request, 'accounts/verify_phone_code.html', {'phone_number': phone_number})
        
        # Verificar el código (nota: la verificación real se hace del lado del cliente con Firebase)
        # Aquí solo simulamos la verificación para demostración
        if len(code) == 6 and code.isdigit():
            try:
                # Buscar usuario y actualizar contraseña
                user = User.objects.get(telefono=phone_number)
                user.set_password(new_password)
                user.save()
                
                # Limpiar sesión
                del request.session['password_reset_phone']
                
                messages.success(request, 'Contraseña actualizada exitosamente. Ya puedes iniciar sesión.')
                return redirect('login')
            except User.DoesNotExist:
                messages.error(request, 'Usuario no encontrado')
        else:
            messages.error(request, 'Código de verificación inválido')
    
    context = {
        'phone_number': phone_number
    }
    return render(request, 'accounts/verify_phone_code.html', context)


@csrf_exempt
@require_http_methods(["POST"])
def verify_phone_code_ajax(request):
    """
    Vista AJAX para verificar el código de SMS
    """
    try:
        data = json.loads(request.body)
        phone_number = data.get('phone_number')
        code = data.get('code')
        
        if not phone_number or not code:
            return JsonResponse({
                'success': False,
                'error': 'Datos incompletos'
            }, status=400)
        
        # Verificar el código con Firebase
        is_valid = FirebaseAuthService.verify_phone_code(phone_number, code)
        
        if is_valid:
            return JsonResponse({
                'success': True,
                'message': 'Código verificado correctamente'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Código inválido'
            }, status=400)
            
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Datos inválidos'
        }, status=400)
    except Exception as e:
        print(f"Error en verify_phone_code_ajax: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

