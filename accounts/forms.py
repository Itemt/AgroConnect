from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, ProducerProfile, BuyerProfile
from core.colombia_locations import get_departments, get_all_cities, COLOMBIA_LOCATIONS
from core.country_codes import get_country_codes
from core.models import Farm
import requests
import time
import logging
from io import BytesIO
from django.core.files import File
from django.core.files.base import ContentFile

logger = logging.getLogger(__name__)

def download_google_profile_image(photo_url, user):
    """
    Descarga la imagen de perfil de Google y la guarda en el campo profile_image del usuario
    """
    if not photo_url:
        return False
    
    try:
        # Descargar la imagen
        response = requests.get(photo_url, timeout=10)
        response.raise_for_status()
        
        # Obtener el nombre del archivo de la URL o generar uno
        filename = f"google_profile_{user.id}_{int(time.time())}.jpg"
        
        # Crear un archivo en memoria
        image_file = ContentFile(response.content)
        
        # Guardar en el campo profile_image
        user.profile_image.save(filename, image_file, save=True)
        
        logger.info(f"Imagen de perfil de Google descargada y guardada para usuario {user.email}")
        return True
    except Exception as e:
        logger.error(f"Error descargando imagen de perfil de Google: {str(e)}")
        return False


class BuyerRegistrationForm(forms.ModelForm):
    """Formulario de registro para compradores (sin campos de finca)"""
    # Campos básicos
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Nombres",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tus nombres',
            'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo se permiten letras y espacios',
            'oninput': 'this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "")'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Apellidos",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tus apellidos',
            'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo se permiten letras y espacios',
            'oninput': 'this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "")'
        })
    )
    email = forms.EmailField(
        required=True, 
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'tu@email.com'
        })
    )
    cedula = forms.CharField(
        max_length=20, 
        required=True, 
        label="Cédula",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Ej: 12345678',
            'type': 'number',
            'pattern': '[0-9]+',
            'title': 'Solo se permiten números',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "")'
        }),
        help_text="Número de cédula de identidad"
    )
    telefono = forms.CharField(
        max_length=20, 
        required=True, 
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': '+57 320 123 4567',
            'type': 'tel',
            'pattern': '\\+?[0-9\\s\\-()]+',
            'title': 'Formato: +57 320 123 4567'
        }),
        help_text="Número de teléfono de contacto"
    )
    
    # Campos de contraseña (solo para registro normal)
    password1 = forms.CharField(
        required=False,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tu contraseña'
        })
    )
    password2 = forms.CharField(
        required=False,
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Confirma tu contraseña'
        })
    )
    
    # Campos de ubicación
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'data-cities-url': '/ajax/cities/'
        }),
        label="Departamento",
        required=False
    )
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
        }),
        label="Ciudad/Municipio",
        required=False
    )
    
    def __init__(self, *args, **kwargs):
        # Unificar inicialización para evitar duplicados y pérdidas de lógica
        is_google_signup = kwargs.pop('is_google_signup', False)
        super().__init__(*args, **kwargs)

        # Guardar flag para validaciones posteriores
        self.is_google_signup = is_google_signup

        # Configurar widgets de contraseña y visibilidad según el flujo
        if self.is_google_signup:
            # Para usuarios de Google, hacer campos de contraseña obligatorios
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['password1'].label = "Contraseña"
            self.fields['password2'].label = "Confirmar Contraseña"
            self.fields['password1'].help_text = "Asigna una contraseña para poder iniciar sesión con tu nombre de usuario"
            self.fields['password2'].help_text = "Confirma tu contraseña"
        else:
            self.fields['password1'].required = True
            self.fields['password2'].required = True

        self.fields['password1'].widget.attrs.update({
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Mínimo 8 caracteres'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Confirma tu contraseña'
        })
        self.fields['username'].widget.attrs.update({
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Nombre de usuario único'
        })

        # Poblar opciones de ciudades basado en el departamento seleccionado
        from core.colombia_locations import get_cities_by_department
        departamento_actual = None

        # Prioridad: POST data -> initial -> existing field value
        if self.data and self.data.get('departamento'):
            departamento_actual = self.data.get('departamento')
        elif 'departamento' in self.initial and self.initial.get('departamento'):
            departamento_actual = self.initial.get('departamento')

        if departamento_actual:
            ciudades = get_cities_by_department(departamento_actual)
            self.fields['ciudad'].choices = [('', 'Seleccionar ciudad')] + ciudades
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'cedula', 'telefono', 'departamento', 'ciudad')
    
    def save(self, commit=True, google_photo_url=None):
        # Crear usuario usando User.objects.create_user para manejar contraseñas
        password = self.cleaned_data.get('password1')
        
        if self.is_google_signup:
            # Usuario de Google con contraseña obligatoria
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password1'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                cedula=self.cleaned_data['cedula'],
                telefono=self.cleaned_data['telefono'],
                departamento=self.cleaned_data.get('departamento'),
                ciudad=self.cleaned_data.get('ciudad'),
                role='Comprador',  # Siempre comprador
                has_password=True,
                is_google_user=True
            )
        else:
            # Usuario normal con contraseña requerida
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data.get('password1', 'unusable_password'),
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                cedula=self.cleaned_data['cedula'],
                telefono=self.cleaned_data['telefono'],
                departamento=self.cleaned_data.get('departamento'),
                ciudad=self.cleaned_data.get('ciudad'),
                role='Comprador',  # Siempre comprador
                has_password=True,
                is_google_user=False
            )
        
        # Descargar y guardar imagen de perfil de Google si está disponible
        if self.is_google_signup and google_photo_url:
            download_google_profile_image(google_photo_url, user)
        
        if commit:
            # Crear BuyerProfile
            buyer_profile = BuyerProfile.objects.create(
                user=user,
                departamento=self.cleaned_data.get('departamento'),
                ciudad=self.cleaned_data.get('ciudad')
            )
        return user
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validar contraseñas siempre (tanto para Google como registro normal)
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
            if len(password1) < 8:
                raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")
        else:
            raise forms.ValidationError("Debes completar ambos campos de contraseña.")
        
        return cleaned_data
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("Este nombre de usuario ya está en uso. Por favor, elige otro.")
        return username

class CustomUserCreationForm(UserCreationForm):
    # Campos básicos
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Nombres",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tus nombres',
            'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo se permiten letras y espacios',
            'oninput': 'this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "")'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Apellidos",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tus apellidos',
            'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo se permiten letras y espacios',
            'oninput': 'this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "")'
        })
    )
    email = forms.EmailField(
        required=True, 
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'tu@email.com'
        })
    )
    cedula = forms.CharField(
        max_length=20, 
        required=True, 
        label="Cédula",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Ej: 12345678',
            'type': 'number',
            'pattern': '[0-9]+',
            'title': 'Solo se permiten números',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "")'
        }),
        help_text="Número de cédula de identidad"
    )
    telefono = forms.CharField(
        max_length=20, 
        required=True, 
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': '+57 320 123 4567',
            'type': 'tel',
            'pattern': '\\+?[0-9\\s\\-()]+',
            'title': 'Formato: +57 320 123 4567'
        }),
        help_text="Número de teléfono de contacto"
    )
    
    # Ubicación básica
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-cities-url': '/ajax/cities/'
        }),
        label="Departamento",
        required=True
    )
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Ciudad/Municipio",
        required=True
    )
    
    # NUEVO: Checkbox para vender
    can_sell = forms.BooleanField(
        required=False,
        label="Quiero vender productos",
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500',
            'id': 'id_can_sell'
        }),
        help_text="Marca esta casilla si deseas publicar y vender productos agrícolas"
    )
    
    # Campos de finca (solo requeridos si can_sell=True)
    finca_nombre = forms.CharField(
        max_length=255,
        required=False,
        label="Nombre de la Finca",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Finca El Paraíso'
        })
    )
    finca_departamento = forms.ChoiceField(
        choices=[('', 'Seleccionar departamento')] + get_departments(),
        required=False,
        label="Departamento de la Finca",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_finca_departamento'
        })
    )
    finca_ciudad = forms.ChoiceField(
        choices=[('', 'Primero seleccione un departamento')],
        required=False,
        label="Ciudad/Municipio de la Finca",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_finca_ciudad'
        })
    )
    finca_direccion = forms.CharField(
        required=False,
        label="Dirección de la Finca",
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 2,
            'placeholder': 'Dirección completa de la finca'
        })
    )
    finca_area_total = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Área Total (hectáreas)",
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.01',
            'min': '0.01',
            'placeholder': 'Ej: 5.5'
        })
    )
    finca_area_cultivable = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        label="Área Cultivable (hectáreas)",
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.01',
            'min': '0.01',
            'placeholder': 'Ej: 4.0'
        })
    )
    finca_tipo_suelo = forms.ChoiceField(
        choices=[('', 'Seleccionar tipo de suelo')] + list(Farm.TIPO_SUELO_CHOICES),
        required=False,
        label="Tipo de Suelo",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    finca_tipo_riego = forms.ChoiceField(
        choices=[('', 'Seleccionar tipo de riego')] + list(Farm.TIPO_RIEGO_CHOICES),
        required=False,
        label="Tipo de Riego",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # Campos adicionales del productor
    direccion = forms.CharField(
        max_length=255, 
        required=False, 
        label="Dirección de Residencia",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tu dirección de residencia'
        })
    )
    farm_description = forms.CharField(
        required=False, 
        label="Descripción de tu Experiencia",
        widget=forms.Textarea(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'rows': 3,
            'placeholder': 'Describe tu finca brevemente'
        })
    )
    main_crops = forms.CharField(
        max_length=255, 
        required=False, 
        label="Cultivos Principales",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Ej: Café, Plátano, Aguacate'
        })
    )
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            # Validar que no contenga números
            if any(char.isdigit() for char in first_name):
                raise forms.ValidationError('Los nombres no pueden contener números.')
            
            # Validar que solo contenga letras y espacios
            if not all(char.isalpha() or char.isspace() for char in first_name):
                raise forms.ValidationError('Los nombres solo pueden contener letras y espacios.')
        
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            # Validar que no contenga números
            if any(char.isdigit() for char in last_name):
                raise forms.ValidationError('Los apellidos no pueden contener números.')
            
            # Validar que solo contenga letras y espacios
            if not all(char.isalpha() or char.isspace() for char in last_name):
                raise forms.ValidationError('Los apellidos solo pueden contener letras y espacios.')
        
        return last_name
    
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula:
            # Validar que solo contenga números
            if not cedula.isdigit():
                raise forms.ValidationError('La cédula debe contener solo números.')
            
            # Validar longitud mínima
            if len(cedula) < 6:
                raise forms.ValidationError('La cédula debe tener al menos 6 dígitos.')
            
            # Validar cédula única (sin revelar información sensible)
            if User.objects.filter(cedula=cedula).exists():
                raise forms.ValidationError('Esta cédula no está disponible. Por favor, verifica los datos ingresados.')
        
        return cedula
    
    def clean(self):
        cleaned_data = super().clean()
        can_sell = cleaned_data.get('can_sell')
        direccion = cleaned_data.get('direccion')
        farm_description = cleaned_data.get('farm_description')
        main_crops = cleaned_data.get('main_crops')
        
        # Si quiere vender, los campos de finca son requeridos
        if can_sell:
            if not direccion:
                self.add_error('direccion', 'Este campo es obligatorio si deseas vender productos.')
            if not farm_description:
                self.add_error('farm_description', 'Este campo es obligatorio si deseas vender productos.')
            if not main_crops:
                self.add_error('main_crops', 'Este campo es obligatorio si deseas vender productos.')
        
        return cleaned_data

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'cedula', 'telefono', 'can_sell', 'departamento', 'ciudad', 'direccion', 'farm_description', 'main_crops', 'password1', 'password2')
        labels = {
            'username': 'Nombre de Usuario',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña'
        }
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Tu nombre de usuario'
            }),
            'first_name': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Tus nombres'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Tus apellidos'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'tu@email.com'
            }),
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_',
            'password1': 'Tu contraseña debe tener al menos 8 caracteres.',
            'password2': 'Ingresa la misma contraseña que antes, para verificación.'
        }
        error_messages = {
            'username': {
                'unique': 'Ya existe un usuario con ese nombre de usuario.',
                'invalid': 'Ingresa un nombre de usuario válido. Este valor puede contener solo letras, números y los caracteres @/./+/-/_.',
                'required': 'Este campo es obligatorio.',
            },
            'password1': {
                'required': 'Este campo es obligatorio.',
            },
            'password2': {
                'required': 'Este campo es obligatorio.',
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar clases CSS a los campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Mínimo 8 caracteres'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Repite tu contraseña'
        })
        
        if 'departamento' in self.data:
            try:
                departamento = self.data.get('departamento')
                cities = COLOMBIA_LOCATIONS.get(departamento, [])
                self.fields['ciudad'].choices = [(city, city) for city in sorted(cities)]
            except (ValueError, TypeError):
                pass

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 8:
                raise ValidationError('Tu contraseña debe tener al menos 8 caracteres.')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Las contraseñas no coinciden.')
        return password2
    
    def clean(self):
        cleaned_data = super().clean()
        can_sell = cleaned_data.get('can_sell')
        area_total = cleaned_data.get('finca_area_total')
        area_cultivable = cleaned_data.get('finca_area_cultivable')
        
        # Si quiere vender, validar campos de finca
        if can_sell:
            required_finca_fields = [
                'finca_nombre', 'finca_departamento', 'finca_ciudad', 'finca_direccion',
                'finca_area_total', 'finca_area_cultivable', 'finca_tipo_suelo', 'finca_tipo_riego'
            ]
            
            for field in required_finca_fields:
                if not cleaned_data.get(field):
                    raise ValidationError(f"Si quieres vender, el campo '{self.fields[field].label}' es obligatorio.")
        
        # Validar área cultivable vs área total
        if area_total and area_cultivable:
            if area_cultivable > area_total:
                raise ValidationError(
                    "El área cultivable no puede ser mayor que el área total de la finca."
                )
        
        return cleaned_data


class BuyerEditForm(forms.ModelForm):
    """Formulario completo de edición de perfil para compradores"""
    
    # Campos de usuario
    username = forms.CharField(
        max_length=150,
        required=False,
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Tu nombre de usuario único'
        })
    )
    email = forms.EmailField(
        required=False,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'tu@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label="Nombres",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Tus nombres'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label="Apellidos",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Tus apellidos'
        })
    )
    cedula = forms.CharField(
        max_length=20,
        required=False,
        label="Cédula",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Ej: 12345678',
            'type': 'text',
            'pattern': '[0-9]+',
            'title': 'Solo se permiten números',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "")'
        }),
        help_text="Número de cédula de identidad"
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': '+57 320 123 4567',
            'type': 'tel',
            'pattern': '\\+?[0-9\\s\\-()]+',
            'title': 'Formato: +57 320 123 4567'
        }),
        help_text="Número de teléfono con código de país (+57 para Colombia)"
    )
    pais = forms.ChoiceField(
        choices=get_country_codes(),
        required=False,
        label="País",
        widget=forms.Select(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'id': 'id_pais'
        }),
        help_text="Selecciona tu país para el número de teléfono"
    )
    profile_image = forms.ImageField(
        required=False,
        label="Foto de Perfil",
        widget=forms.ClearableFileInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'accept': 'image/*'
        }),
        help_text="Sube una foto para tu perfil (opcional)"
    )
    
    # Campos de ubicación del comprador
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'id': 'id_departamento'
        }),
        label="Departamento",
        required=False
    )
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'id': 'id_ciudad'
        }),
        label="Ciudad/Municipio",
        required=False
    )
    
    # Campos de contraseña
    new_password = forms.CharField(
        required=False,
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Mínimo 8 caracteres'
        }),
        help_text="Mínimo 8 caracteres"
    )
    confirm_password = forms.CharField(
        required=False,
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Confirma tu nueva contraseña'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar datos iniciales del usuario
        if self.instance.pk:
            self.fields['username'].initial = self.instance.username
            self.fields['email'].initial = self.instance.email
            self.fields['first_name'].initial = self.instance.first_name
            self.fields['last_name'].initial = self.instance.last_name
            self.fields['cedula'].initial = self.instance.cedula
            # Formatear número de teléfono con código de país si no lo tiene
            telefono = self.instance.telefono
            if telefono and not telefono.startswith('+57'):
                # Si el número empieza con 3 y tiene 10 dígitos, agregar +57
                if telefono.startswith('3') and len(telefono) == 10:
                    telefono = f"+57{telefono}"
                # Si el número empieza con 57 y tiene 12 dígitos, agregar +
                elif telefono.startswith('57') and len(telefono) == 12:
                    telefono = f"+{telefono}"
            self.fields['telefono'].initial = telefono
            self.fields['pais'].initial = self.instance.pais
            self.fields['departamento'].initial = self.instance.departamento
            self.fields['ciudad'].initial = self.instance.ciudad
            
            # Cargar ciudades del departamento actual
            if self.instance.departamento:
                from core.colombia_locations import get_cities_by_department
                ciudades = get_cities_by_department(self.instance.departamento)
                self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + ciudades
                # Asegurar que el valor inicial de la ciudad se mantenga
                if self.instance.ciudad:
                    self.fields['ciudad'].initial = self.instance.ciudad
            else:
                # Si no hay departamento, limpiar las opciones de ciudad
                self.fields['ciudad'].choices = [('', 'Selecciona primero un departamento')]
        
        # Si hay datos POST, cargar ciudades del departamento seleccionado
        if self.data and 'departamento' in self.data:
            departamento = self.data.get('departamento')
            if departamento:
                from core.colombia_locations import get_cities_by_department
                ciudades = get_cities_by_department(departamento)
                self.fields['ciudad'].choices = [('', 'Seleccionar ciudad')] + ciudades
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and self.instance.pk:
            # Verificar que el username no esté en uso por otro usuario
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.instance.pk:
            # Verificar que el email no esté en uso por otro usuario
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Este correo electrónico ya está en uso.')
        return email
    
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula and self.instance.pk:
            # Verificar que la cédula no esté en uso por otro usuario
            if User.objects.filter(cedula=cedula).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Esta cédula ya está registrada por otro usuario.')
        return cedula
    
    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if new_password:
            if not confirm_password:
                raise forms.ValidationError('Debes confirmar tu nueva contraseña.')
            if new_password != confirm_password:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return confirm_password
    
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if new_password and len(new_password) < 8:
            raise forms.ValidationError('La nueva contraseña debe tener al menos 8 caracteres.')
        return new_password
    
    def save(self, commit=True):
        # Actualizar datos del usuario
        self.instance.username = self.cleaned_data.get('username')
        self.instance.email = self.cleaned_data.get('email')
        self.instance.first_name = self.cleaned_data.get('first_name')
        self.instance.last_name = self.cleaned_data.get('last_name')
        self.instance.cedula = self.cleaned_data.get('cedula')
        # Normalizar número de teléfono
        telefono = self.cleaned_data.get('telefono')
        if telefono:
            # Remover espacios y caracteres especiales excepto +
            telefono = telefono.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
            # Si empieza con +57, mantenerlo
            if telefono.startswith('+57'):
                self.instance.telefono = telefono
            # Si empieza con 57 y tiene 12 dígitos, agregar +
            elif telefono.startswith('57') and len(telefono) == 12:
                self.instance.telefono = f"+{telefono}"
            # Si empieza con 3 y tiene 10 dígitos, agregar +57
            elif telefono.startswith('3') and len(telefono) == 10:
                self.instance.telefono = f"+57{telefono}"
            else:
                self.instance.telefono = telefono
        else:
            self.instance.telefono = telefono
        self.instance.pais = self.cleaned_data.get('pais')
        self.instance.departamento = self.cleaned_data.get('departamento')
        self.instance.ciudad = self.cleaned_data.get('ciudad')
        
        # Actualizar foto de perfil si se proporciona
        if self.cleaned_data.get('profile_image'):
            self.instance.profile_image = self.cleaned_data.get('profile_image')
        
        # Cambiar contraseña si se proporciona
        new_password = self.cleaned_data.get('new_password')
        if new_password:
            self.instance.set_password(new_password)
        
        if commit:
            self.instance.save()
            
            # Actualizar BuyerProfile
            buyer_profile, created = BuyerProfile.objects.get_or_create(user=self.instance)
            buyer_profile.departamento = self.cleaned_data.get('departamento')
            buyer_profile.ciudad = self.cleaned_data.get('ciudad')
            buyer_profile.save()
        
        return self.instance
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'cedula', 'telefono', 'departamento', 'ciudad', 'profile_image']

class UserEditForm(forms.ModelForm):
    cedula = forms.CharField(
        max_length=20, 
        required=True, 
        label="Cédula",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ej: 12345678',
            'type': 'number',
            'pattern': '[0-9]+',
            'title': 'Solo se permiten números',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "")'
        }),
        help_text="Número de cédula de identidad"
    )
    telefono = forms.CharField(
        max_length=20, 
        required=False, 
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+57 320 123 4567',
            'type': 'tel',
            'pattern': '\\+?[0-9\\s\\-()]+',
            'title': 'Formato: +57 320 123 4567'
        }),
        help_text="Número de teléfono de contacto"
    )
    
    can_sell = forms.BooleanField(
        required=False,
        label="Quiero vender productos",
        widget=forms.CheckboxInput(attrs={
            'class': 'w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500',
        }),
        help_text="Marca esta casilla si deseas publicar y vender productos agrícolas"
    )
    
    # Campos de ubicación
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-cities-url': '/ajax/cities/'
        }),
        label="Departamento",
        required=False
    )
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'form-select',
        }),
        label="Ciudad/Municipio",
        required=False
    )
    
    # Campos de vendedor (opcionales)
    direccion = forms.CharField(
        max_length=255, 
        required=False, 
        label="Dirección de la Finca",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Vereda La Esperanza, Finca Los Naranjos'
        })
    )
    farm_description = forms.CharField(
        required=False, 
        label="Descripción de la Finca",
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 3,
            'placeholder': 'Describe tu finca brevemente'
        })
    )
    main_crops = forms.CharField(
        max_length=255, 
        required=False, 
        label="Cultivos Principales",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Café, Plátano, Aguacate'
        })
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Pre-cargar datos si existen perfiles
        if self.instance.pk:
            # Cargar datos de BuyerProfile si existe
            try:
                buyer_profile = self.instance.buyer_profile
                self.fields['departamento'].initial = buyer_profile.departamento
                self.fields['ciudad'].initial = buyer_profile.ciudad
                
                # Cargar ciudades del departamento
                if buyer_profile.departamento:
                    cities = COLOMBIA_LOCATIONS.get(buyer_profile.departamento, [])
                    self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]
            except:
                pass
            
            # Cargar datos de ProducerProfile si existe
            try:
                producer_profile = self.instance.producer_profile
                self.fields['direccion'].initial = producer_profile.direccion
                self.fields['farm_description'].initial = producer_profile.farm_description
                self.fields['main_crops'].initial = producer_profile.main_crops
            except:
                pass
        
        # Si hay data del POST, actualizar ciudades
        if 'departamento' in self.data:
            try:
                departamento = self.data.get('departamento')
                cities = COLOMBIA_LOCATIONS.get(departamento, [])
                self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]
            except (ValueError, TypeError):
                pass
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get('first_name')
        if first_name:
            if any(char.isdigit() for char in first_name):
                raise forms.ValidationError('Los nombres no pueden contener números.')
            if not all(char.isalpha() or char.isspace() for char in first_name):
                raise forms.ValidationError('Los nombres solo pueden contener letras y espacios.')
        return first_name
    
    def clean_last_name(self):
        last_name = self.cleaned_data.get('last_name')
        if last_name:
            if any(char.isdigit() for char in last_name):
                raise forms.ValidationError('Los apellidos no pueden contener números.')
            if not all(char.isalpha() or char.isspace() for char in last_name):
                raise forms.ValidationError('Los apellidos solo pueden contener letras y espacios.')
        return last_name
    
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula:
            if not cedula.isdigit():
                raise forms.ValidationError('La cédula debe contener solo números.')
            if len(cedula) < 6:
                raise forms.ValidationError('La cédula debe tener al menos 6 dígitos.')
            if User.objects.filter(cedula=cedula).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('Esta cédula no está disponible. Por favor, verifica los datos ingresados.')
        return cedula
    
    def clean(self):
        cleaned_data = super().clean()
        can_sell = cleaned_data.get('can_sell')
        direccion = cleaned_data.get('direccion')
        farm_description = cleaned_data.get('farm_description')
        main_crops = cleaned_data.get('main_crops')
        
        # Si quiere vender, los campos de finca son requeridos
        if can_sell:
            if not direccion:
                self.add_error('direccion', 'Este campo es obligatorio si deseas vender productos.')
            if not farm_description:
                self.add_error('farm_description', 'Este campo es obligatorio si deseas vender productos.')
            if not main_crops:
                self.add_error('main_crops', 'Este campo es obligatorio si deseas vender productos.')
        
        return cleaned_data
    
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'cedula', 'can_sell', 'profile_image')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'profile_image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'cedula': 'Cédula',
            'profile_image': 'Imagen de Perfil',
        }


class AdminUserEditForm(UserEditForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    is_active = forms.BooleanField(required=False, label="Activo")
    is_staff = forms.BooleanField(required=False, label="Staff (Admin)")

    class Meta(UserEditForm.Meta):
        fields = ('first_name', 'last_name', 'email', 'cedula', 'role', 'is_active', 'is_staff', 'profile_image')


class ProducerProfileForm(forms.ModelForm):
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'data-cities-url': '/ajax/cities/'  # Corrected URL
        }),
        label="Departamento",
        required=True
    )

    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_ciudad'
        }),
        label="Ciudad/Municipio",
        required=True
    )

    class Meta:
        model = ProducerProfile
        fields = ['departamento', 'ciudad', 'direccion', 'farm_description', 'main_crops']
        widgets = {
            'direccion': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Vereda La Esperanza, Finca Los Naranjos'
            }),
            'farm_description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 4,
                'placeholder': 'Describe tu finca: tamaño, tipo de cultivos, métodos utilizados, etc.'
            }),
            'main_crops': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Café, Plátano, Aguacate'
            })
        }
        labels = {
            'direccion': 'Dirección específica (opcional)',
            'farm_description': 'Descripción de la finca',
            'main_crops': 'Cultivos principales'
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically set city choices based on department
        if 'departamento' in self.data:
            try:
                departamento = self.data.get('departamento')
                cities = COLOMBIA_LOCATIONS.get(departamento, [])
                self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]
            except (ValueError, TypeError):
                pass  # Handle cases where department is not valid
        elif self.instance.pk and self.instance.departamento:
            # For existing instances, populate cities based on the saved department
            cities = COLOMBIA_LOCATIONS.get(self.instance.departamento, [])
            self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]


class ProducerProfileEditForm(forms.ModelForm):
    """Formulario completo de edición de perfil para productores"""
    
    # Campos de usuario
    username = forms.CharField(
        max_length=150,
        required=False,
        label="Nombre de Usuario",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Tu nombre de usuario único'
        })
    )
    email = forms.EmailField(
        required=False,
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'tu@email.com'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        label="Nombres",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Tus nombres'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        label="Apellidos",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Tus apellidos'
        })
    )
    cedula = forms.CharField(
        max_length=20,
        required=False,
        label="Cédula",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Ej: 12345678',
            'type': 'text',
            'pattern': '[0-9]+',
            'title': 'Solo se permiten números',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "")'
        }),
        help_text="Número de cédula de identidad"
    )
    telefono = forms.CharField(
        max_length=20,
        required=False,
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': '+57 320 123 4567',
            'type': 'tel',
            'pattern': '\\+?[0-9\\s\\-()]+',
            'title': 'Formato: +57 320 123 4567'
        }),
        help_text="Número de teléfono con código de país (+57 para Colombia)"
    )
    pais = forms.ChoiceField(
        choices=get_country_codes(),
        required=False,
        label="País",
        widget=forms.Select(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'id': 'id_pais'
        }),
        help_text="Selecciona tu país para el número de teléfono"
    )
    profile_image = forms.ImageField(
        required=False,
        label="Foto de Perfil",
        widget=forms.ClearableFileInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'accept': 'image/*'
        }),
        help_text="Sube una foto para tu perfil (opcional)"
    )
    
    # Campos de ubicación del vendedor
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'id': 'id_departamento'
        }),
        label="Departamento",
        required=False
    )
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'id': 'id_ciudad'
        }),
        label="Ciudad/Municipio",
        required=False
    )
    
    # Campos de contraseña
    new_password = forms.CharField(
        required=False,
        label="Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Mínimo 8 caracteres'
        }),
        help_text="Mínimo 8 caracteres"
    )
    confirm_password = forms.CharField(
        required=False,
        label="Confirmar Nueva Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Confirma tu nueva contraseña'
        })
    )
    
    # Campos específicos del productor
    direccion = forms.CharField(
        max_length=255,
        required=False,
        label="Dirección de la Finca",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Ej: Vereda La Esperanza, Finca Los Naranjos'
        }),
        help_text="Dirección específica de tu finca (opcional)"
    )
    farm_description = forms.CharField(
        required=False,
        label="Descripción de la Finca",
        widget=forms.Textarea(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'rows': 4,
            'placeholder': 'Describe tu finca, tipo de terreno, etc.'
        }),
        help_text="Información adicional sobre tu finca (opcional)"
    )
    main_crops = forms.CharField(
        max_length=255,
        required=False,
        label="Cultivos Principales",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
            'placeholder': 'Ej: Papa, Maíz, Tomate'
        }),
        help_text="Principales cultivos de tu finca (opcional)"
    )
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Cargar datos iniciales del usuario
        if self.user:
            self.fields['username'].initial = self.user.username
            self.fields['email'].initial = self.user.email
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name
            self.fields['cedula'].initial = self.user.cedula
            # Formatear número de teléfono con código de país si no lo tiene
            telefono = self.user.telefono
            if telefono and not telefono.startswith('+57'):
                # Si el número empieza con 3 y tiene 10 dígitos, agregar +57
                if telefono.startswith('3') and len(telefono) == 10:
                    telefono = f"+57{telefono}"
                # Si el número empieza con 57 y tiene 12 dígitos, agregar +
                elif telefono.startswith('57') and len(telefono) == 12:
                    telefono = f"+{telefono}"
            self.fields['telefono'].initial = telefono
            self.fields['pais'].initial = self.user.pais
            self.fields['departamento'].initial = self.user.departamento
            self.fields['ciudad'].initial = self.user.ciudad
            
            # Cargar ciudades del departamento actual
            if self.user.departamento:
                from core.colombia_locations import get_cities_by_department
                ciudades = get_cities_by_department(self.user.departamento)
                self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + ciudades
                # Asegurar que el valor inicial de la ciudad se mantenga
                if self.user.ciudad:
                    self.fields['ciudad'].initial = self.user.ciudad
            else:
                # Si no hay departamento, limpiar las opciones de ciudad
                self.fields['ciudad'].choices = [('', 'Selecciona primero un departamento')]
            
            # Cargar datos del ProducerProfile si existe
            try:
                producer_profile = self.user.producer_profile
                self.fields['direccion'].initial = producer_profile.direccion
                self.fields['farm_description'].initial = producer_profile.farm_description
                self.fields['main_crops'].initial = producer_profile.main_crops
            except AttributeError:
                # Si no tiene producer_profile, usar valores por defecto
                pass
        
        # Si hay datos POST, cargar ciudades del departamento seleccionado
        if self.data and 'departamento' in self.data:
            departamento = self.data.get('departamento')
            if departamento:
                from core.colombia_locations import get_cities_by_department
                ciudades = get_cities_by_department(departamento)
                self.fields['ciudad'].choices = [('', 'Seleccionar ciudad')] + ciudades
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username and self.user:
            # Verificar que el username no esté en uso por otro usuario
            if User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError('Este nombre de usuario ya está en uso.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and self.user:
            # Verificar que el email no esté en uso por otro usuario
            if User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError('Este correo electrónico ya está en uso.')
        return email
    
    def clean_cedula(self):
        cedula = self.cleaned_data.get('cedula')
        if cedula and self.user:
            # Verificar que la cédula no esté en uso por otro usuario
            if User.objects.filter(cedula=cedula).exclude(pk=self.user.pk).exists():
                raise forms.ValidationError('Esta cédula ya está registrada por otro usuario.')
        return cedula
    
    def clean_confirm_password(self):
        new_password = self.cleaned_data.get('new_password')
        confirm_password = self.cleaned_data.get('confirm_password')
        
        if new_password:
            if not confirm_password:
                raise forms.ValidationError('Debes confirmar tu nueva contraseña.')
            if new_password != confirm_password:
                raise forms.ValidationError('Las contraseñas no coinciden.')
        
        return confirm_password
    
    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if new_password and len(new_password) < 8:
            raise forms.ValidationError('La nueva contraseña debe tener al menos 8 caracteres.')
        return new_password
    
    def save(self, commit=True):
        # Actualizar datos del usuario
        if self.user:
            self.user.username = self.cleaned_data.get('username')
            self.user.email = self.cleaned_data.get('email')
            self.user.first_name = self.cleaned_data.get('first_name')
            self.user.last_name = self.cleaned_data.get('last_name')
            self.user.cedula = self.cleaned_data.get('cedula')
            # Normalizar número de teléfono
            telefono = self.cleaned_data.get('telefono')
            if telefono:
                # Remover espacios y caracteres especiales excepto +
                telefono = telefono.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
                # Si empieza con +57, mantenerlo
                if telefono.startswith('+57'):
                    self.user.telefono = telefono
                # Si empieza con 57 y tiene 12 dígitos, agregar +
                elif telefono.startswith('57') and len(telefono) == 12:
                    self.user.telefono = f"+{telefono}"
                # Si empieza con 3 y tiene 10 dígitos, agregar +57
                elif telefono.startswith('3') and len(telefono) == 10:
                    self.user.telefono = f"+57{telefono}"
                else:
                    self.user.telefono = telefono
            else:
                self.user.telefono = telefono
            self.user.pais = self.cleaned_data.get('pais')
            self.user.departamento = self.cleaned_data.get('departamento')
            self.user.ciudad = self.cleaned_data.get('ciudad')
            
            # Actualizar foto de perfil si se proporciona
            if self.cleaned_data.get('profile_image'):
                self.user.profile_image = self.cleaned_data.get('profile_image')
            
            # Cambiar contraseña si se proporciona
            new_password = self.cleaned_data.get('new_password')
            if new_password:
                self.user.set_password(new_password)
            
            if commit:
                self.user.save()
                
                # Actualizar ProducerProfile
                producer_profile, created = ProducerProfile.objects.get_or_create(user=self.user)
                producer_profile.departamento = self.cleaned_data.get('departamento')
                producer_profile.ciudad = self.cleaned_data.get('ciudad')
                producer_profile.direccion = self.cleaned_data.get('direccion')
                producer_profile.farm_description = self.cleaned_data.get('farm_description')
                producer_profile.main_crops = self.cleaned_data.get('main_crops')
                producer_profile.save()
        
        return self.user
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'cedula', 'telefono', 'departamento', 'ciudad', 'profile_image']
        widgets = {
            'direccion': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Ej: Vereda La Esperanza, Finca Los Naranjos'
            }),
            'farm_description': forms.Textarea(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'rows': 4,
                'placeholder': 'Describe tu finca: tamaño, tipo de cultivos, métodos utilizados, etc.'
            }),
            'main_crops': forms.TextInput(attrs={
                'class': 'block w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Ej: Café, Plátano, Aguacate'
            })
        }
        labels = {
            'direccion': 'Dirección de la Finca',
            'farm_description': 'Descripción de la Finca',
            'main_crops': 'Cultivos Principales'
        }


class BuyerProfileForm(forms.ModelForm):
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_departamento_buyer',
            'data-cities-url': '/ajax/cities/'  # Corrected URL
        }),
        label="Departamento",
        required=True
    )

    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_ciudad_buyer'
        }),
        label="Ciudad/Municipio",
        required=True
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Dynamically set city choices based on department
        if 'departamento' in self.data:
            try:
                departamento = self.data.get('departamento')
                cities = COLOMBIA_LOCATIONS.get(departamento, [])
                self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.departamento:
            cities = COLOMBIA_LOCATIONS.get(self.instance.departamento, [])
            self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]

    class Meta:
        model = BuyerProfile
        fields = ['company_name', 'business_type', 'departamento', 'ciudad']
        widgets = {
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre de tu empresa o negocio'
            }),
            'business_type': forms.Select(attrs={
                'class': 'form-control'
            }, choices=[
                ('', 'Selecciona el tipo de negocio'),
                ('Restaurante', 'Restaurante'),
                ('Supermercado', 'Supermercado'),
                ('Distribuidor', 'Distribuidor'),
                ('Tienda Local', 'Tienda Local'),
                ('Mercado', 'Mercado'),
                ('Exportador', 'Exportador'),
                ('Procesador', 'Procesador de Alimentos'),
                ('Otro', 'Otro')
            ])
        }
        labels = {
            'company_name': 'Nombre de la empresa',
            'business_type': 'Tipo de negocio'
        }


class ProducerRegistrationForm(forms.ModelForm):
    """Formulario de registro para productores con finca inicial"""
    # Campos básicos
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Nombres",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tus nombres',
            'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo se permiten letras y espacios',
            'oninput': 'this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "")'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Apellidos",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tus apellidos',
            'pattern': '[a-zA-ZáéíóúÁÉÍÓÚñÑ\s]+',
            'title': 'Solo se permiten letras y espacios',
            'oninput': 'this.value = this.value.replace(/[^a-zA-ZáéíóúÁÉÍÓÚñÑ\s]/g, "")'
        })
    )
    email = forms.EmailField(
        required=True, 
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'tu@email.com'
        })
    )
    cedula = forms.CharField(
        max_length=20, 
        required=True, 
        label="Cédula",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tu número de cédula',
            'pattern': '[0-9]+',
            'title': 'Solo se permiten números',
            'oninput': 'this.value = this.value.replace(/[^0-9]/g, "")'
        })
    )
    telefono = forms.CharField(
        max_length=20, 
        required=True, 
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': '+57 320 123 4567',
            'pattern': '\\+?[0-9\\s\\-()]+',
            'title': 'Formato: +57 320 123 4567'
        })
    )
    
    # Campos de contraseña (solo para registro normal)
    password1 = forms.CharField(
        required=False,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Tu contraseña'
        })
    )
    password2 = forms.CharField(
        required=False,
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Confirma tu contraseña'
        })
    )
    
    # Campos de la finca
    finca_nombre = forms.CharField(
        max_length=100, 
        required=True, 
        label="Nombre de la Finca",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Nombre de tu finca'
        })
    )
    finca_departamento = forms.ChoiceField(
        required=True, 
        label="Departamento",
        choices=[('', 'Selecciona un departamento')] + [(dept, dept) for dept in sorted(get_departments())],
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'onchange': 'updateCities()'
        })
    )
    finca_ciudad = forms.ChoiceField(
        required=True, 
        label="Ciudad",
        choices=[('', 'Primero selecciona un departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
        })
    )
    finca_direccion = forms.CharField(
        max_length=200, 
        required=True, 
        label="Dirección de la Finca",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Dirección completa de tu finca'
        })
    )
    finca_area = forms.DecimalField(
        required=True, 
        label="Área Total (hectáreas)",
        min_value=0.01,
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': '0.00',
            'step': '0.01',
            'min': '0.01'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
                'placeholder': 'Nombre de usuario único'
            })
        }

    def __init__(self, *args, **kwargs):
        self.is_google_signup = kwargs.pop('is_google_signup', False)
        super().__init__(*args, **kwargs)
        
        # Si es registro con Google, hacer campos de contraseña obligatorios
        if self.is_google_signup:
            self.fields['password1'].required = True
            self.fields['password2'].required = True
            self.fields['password1'].label = "Contraseña"
            self.fields['password2'].label = "Confirmar Contraseña"
            self.fields['password1'].help_text = "Asigna una contraseña para poder iniciar sesión con tu nombre de usuario"
            self.fields['password2'].help_text = "Confirma tu contraseña"
        else:
            # Si es registro normal, hacer contraseñas requeridas
            self.fields['password1'].required = True
            self.fields['password2'].required = True

    def clean(self):
        cleaned_data = super().clean()
        
        # Validar contraseñas siempre (tanto para Google como registro normal)
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Las contraseñas no coinciden.")
            try:
                validate_password(password1)
            except ValidationError as e:
                raise forms.ValidationError(e.messages)
        else:
            raise forms.ValidationError("Debes completar ambos campos de contraseña.")
        
        return cleaned_data

    def save(self, commit=True):
        # Crear usuario
        password = self.cleaned_data.get('password1')
        
        if self.is_google_signup:
            # Usuario de Google con contraseña obligatoria
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password1'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                has_password=True,
                is_google_user=True
            )
        else:
            # Usuario normal con contraseña requerida
            user = User.objects.create_user(
                username=self.cleaned_data['username'],
                email=self.cleaned_data['email'],
                password=self.cleaned_data['password1'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                has_password=True,
                is_google_user=False
            )
        
        if commit:
            user.save()
            
            # Crear perfil de productor
            ProducerProfile.objects.create(
                user=user,
                cedula=self.cleaned_data['cedula'],
                telefono=self.cleaned_data['telefono']
            )
            
            # Crear finca inicial
            Farm.objects.create(
                user=user,
                nombre=self.cleaned_data['finca_nombre'],
                departamento=self.cleaned_data['finca_departamento'],
                ciudad=self.cleaned_data['finca_ciudad'],
                direccion=self.cleaned_data['finca_direccion'],
                area_total=self.cleaned_data['finca_area']
            )
        
        return user


class PhonePasswordResetForm(forms.Form):
    """Formulario para recuperación de contraseña por teléfono"""
    telefono = forms.CharField(
        max_length=15,
        required=True,
        label="Número de Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border-2 border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-gray-100 rounded-lg focus:border-green-500 dark:focus:border-green-400 focus:outline-none transition',
            'placeholder': '+57 300 123 4567',
            'type': 'tel'
        }),
        help_text="Ingresa tu número de teléfono con código de país"
    )
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono')
        # Remover espacios y caracteres especiales
        telefono = ''.join(filter(str.isdigit, telefono.replace('+', '')))
        if not telefono:
            raise ValidationError('Por favor ingresa un número de teléfono válido.')
        return '+' + telefono if not telefono.startswith('+') else telefono