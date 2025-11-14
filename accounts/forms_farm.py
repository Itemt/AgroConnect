from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ProducerProfile, BuyerProfile
from core.models import Farm
from core.colombia_locations import get_departments, get_cities_by_department
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

class ProducerRegistrationForm(forms.ModelForm):
    """Formulario de registro para productores con finca inicial"""
    
    # Campos básicos del usuario
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Nombres",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tus nombres'
        })
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label="Apellidos",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tus apellidos'
        })
    )
    email = forms.EmailField(
        required=True, 
        label="Correo Electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'placeholder': 'tu@email.com'
        })
    )
    cedula = forms.CharField(
        max_length=20, 
        required=True, 
        label="Cédula",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: 12345678'
        })
    )
    telefono = forms.CharField(
        max_length=15,
        required=True,
        label="Teléfono",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: 3001234567'
        })
    )
    
    # Campos de contraseña (solo para registro normal)
    password1 = forms.CharField(
        required=False,
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Tu contraseña'
        })
    )
    password2 = forms.CharField(
        required=False,
        label="Confirmar Contraseña",
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirma tu contraseña'
        })
    )
    
    role = forms.ChoiceField(
        choices=[('Productor', 'Productor')],
        initial='Productor',
        widget=forms.HiddenInput()
    )
    
    # Campos de la finca inicial
    finca_nombre = forms.CharField(
        max_length=255,
        required=True,
        label="Nombre de la Finca",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Finca El Paraíso'
        })
    )
    finca_departamento = forms.ChoiceField(
        choices=[('', 'Seleccionar departamento')] + get_departments(),
        required=True,
        label="Departamento de la Finca",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_finca_departamento'
        })
    )
    finca_ciudad = forms.ChoiceField(
        choices=[('', 'Primero seleccione un departamento')],
        required=True,
        label="Ciudad/Municipio de la Finca",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_finca_ciudad'
        })
    )
    finca_direccion = forms.CharField(
        required=True,
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
        required=True,
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
        required=True,
        label="Área Cultivable (hectáreas)",
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'step': '0.01',
            'min': '0.01',
            'placeholder': 'Ej: 4.0'
        })
    )
    finca_tipo_suelo = forms.ChoiceField(
        choices=Farm.TIPO_SUELO_CHOICES,
        required=True,
        label="Tipo de Suelo",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    finca_tipo_riego = forms.ChoiceField(
        choices=Farm.TIPO_RIEGO_CHOICES,
        required=True,
        label="Tipo de Riego",
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    # Campos de perfil del productor
    direccion = forms.CharField(
        required=True,
        label="Dirección de Residencia",
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 2,
            'placeholder': 'Tu dirección de residencia'
        })
    )
    farm_description = forms.CharField(
        required=False,
        label="Descripción de tu Experiencia",
        widget=forms.Textarea(attrs={
            'class': 'form-input',
            'rows': 3,
            'placeholder': 'Cuéntanos sobre tu experiencia en agricultura'
        })
    )
    main_crops = forms.CharField(
        required=False,
        label="Principales Cultivos",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Tomate, Lechuga, Cebolla'
        })
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'cedula', 'telefono', 'role')
    
    def __init__(self, *args, **kwargs):
        self.is_google_signup = kwargs.pop('is_google_signup', False)
        super().__init__(*args, **kwargs)
        
        # Si es registro con Google, ocultar campos de contraseña
        if self.is_google_signup:
            self.fields['password1'].widget = forms.HiddenInput()
            self.fields['password2'].widget = forms.HiddenInput()
        else:
            # Si es registro normal, hacer contraseñas requeridas
            self.fields['password1'].required = True
            self.fields['password2'].required = True
        self.fields['username'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Tu nombre de usuario'
        })
    
    def clean(self):
        cleaned_data = super().clean()
        area_total = cleaned_data.get('finca_area_total')
        area_cultivable = cleaned_data.get('finca_area_cultivable')
        
        if area_total and area_cultivable:
            if area_cultivable > area_total:
                raise forms.ValidationError(
                    "El área cultivable no puede ser mayor que el área total de la finca."
                )
        
        return cleaned_data
    
    def save(self, commit=True, google_photo_url=None):
        # Crear usuario
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        user.role = 'Productor'
        
        # Manejar contraseña según el tipo de registro
        if self.is_google_signup:
            user.set_unusable_password()
            user.is_google_user = True
        else:
            user.set_password(self.cleaned_data['password1'])
            user.is_google_user = False
        
        if commit:
            user.save()
            
            # Descargar y guardar imagen de perfil de Google si está disponible
            if self.is_google_signup and google_photo_url:
                download_google_profile_image(google_photo_url, user)
            
            # Crear perfil del productor
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
                area_total=self.cleaned_data['finca_area_total'],
                area_cultivable=self.cleaned_data['finca_area_cultivable'],
                tipo_suelo=self.cleaned_data['finca_tipo_suelo'],
                tipo_riego=self.cleaned_data['finca_tipo_riego']
            )
        
        return user

class ProducerProfileEditForm(forms.ModelForm):
    """Formulario extendido para editar perfil de productor con fincas"""
    
    # Campos de finca (opcional para agregar nueva)
    finca_nombre = forms.CharField(
        max_length=255,
        required=False,
        label="Nombre de Nueva Finca",
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Ej: Finca El Paraíso'
        })
    )
    finca_departamento = forms.ChoiceField(
        choices=[('', 'Seleccionar departamento')] + get_departments(),
        required=False,
        label="Departamento de Nueva Finca",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_finca_departamento'
        })
    )
    finca_ciudad = forms.ChoiceField(
        choices=[('', 'Primero seleccione un departamento')],
        required=False,
        label="Ciudad/Municipio de Nueva Finca",
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'id_finca_ciudad'
        })
    )
    finca_direccion = forms.CharField(
        required=False,
        label="Dirección de Nueva Finca",
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
    
    class Meta:
        model = ProducerProfile
        fields = ['direccion', 'farm_description', 'main_crops']
        widgets = {
            'direccion': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Tu dirección de residencia'
            }),
            'farm_description': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Cuéntanos sobre tu experiencia en agricultura'
            }),
            'main_crops': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Ej: Tomate, Lechuga, Cebolla'
            })
        }
        labels = {
            'direccion': 'Dirección de Residencia',
            'farm_description': 'Descripción de tu Experiencia',
            'main_crops': 'Principales Cultivos'
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        area_total = cleaned_data.get('finca_area_total')
        area_cultivable = cleaned_data.get('finca_area_cultivable')
        
        # Validar solo si se están agregando datos de finca
        if any([cleaned_data.get('finca_nombre'), cleaned_data.get('finca_departamento'), 
                cleaned_data.get('finca_ciudad'), cleaned_data.get('finca_direccion')]):
            # Si se está agregando una finca, validar campos requeridos
            required_fields = ['finca_nombre', 'finca_departamento', 'finca_ciudad', 'finca_direccion', 
                             'finca_area_total', 'finca_area_cultivable', 'finca_tipo_suelo', 'finca_tipo_riego']
            for field in required_fields:
                if not cleaned_data.get(field):
                    raise forms.ValidationError(f"Si vas a agregar una finca, el campo '{self.fields[field].label}' es obligatorio.")
        
        if area_total and area_cultivable:
            if area_cultivable > area_total:
                raise forms.ValidationError(
                    "El área cultivable no puede ser mayor que el área total de la finca."
                )
        
        return cleaned_data
    
    def save(self, commit=True):
        profile = super().save(commit=False)
        
        if commit:
            profile.save()
            
            # Crear finca si se proporcionaron datos
            if self.cleaned_data.get('finca_nombre'):
                Farm.objects.create(
                    propietario=self.user,
                    nombre=self.cleaned_data['finca_nombre'],
                    departamento=self.cleaned_data['finca_departamento'],
                    ciudad=self.cleaned_data['finca_ciudad'],
                    direccion=self.cleaned_data['finca_direccion'],
                    area_total=self.cleaned_data['finca_area_total'],
                    area_cultivable=self.cleaned_data['finca_area_cultivable'],
                    tipo_suelo=self.cleaned_data['finca_tipo_suelo'],
                    tipo_riego=self.cleaned_data['finca_tipo_riego']
                )
        
        return profile