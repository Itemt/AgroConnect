from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, ProducerProfile, BuyerProfile
from core.colombia_locations import get_departments, get_all_cities, COLOMBIA_LOCATIONS


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True, label="Nombres")
    last_name = forms.CharField(max_length=30, required=True, label="Apellidos")
    email = forms.EmailField(required=True, label="Correo Electrónico")
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True, label="Tipo de Usuario")

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'password1', 'password2')
        labels = {
            'username': 'Nombre de Usuario',
            'password1': 'Contraseña',
            'password2': 'Confirmar Contraseña'
        }
        help_texts = {
            'username': 'Requerido. 150 caracteres o menos. Solo letras, dígitos y @/./+/-/_',
            'password1': 'Tu contraseña debe tener al menos 6 caracteres.',
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

    def clean_password1(self):
        password1 = self.cleaned_data.get('password1')
        if password1:
            if len(password1) < 6:
                raise ValidationError('Tu contraseña debe tener al menos 6 caracteres.')
        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise ValidationError('Las contraseñas no coinciden.')
        return password2


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico'
        }


class ProducerProfileForm(forms.ModelForm):
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_departamento',
            'onchange': 'updateCities()'
        }),
        label="Departamento",
        required=True
    )
    
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'form-control',
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
                'class': 'form-control',
                'placeholder': 'Ej: Vereda La Esperanza, Finca Los Naranjos'
            }),
            'farm_description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe tu finca: tamaño, tipo de cultivos, métodos utilizados, etc.'
            }),
            'main_crops': forms.TextInput(attrs={
                'class': 'form-control',
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
        
        # Si hay una instancia, configurar las ciudades para el departamento seleccionado
        if self.instance.pk and self.instance.departamento:
            cities = COLOMBIA_LOCATIONS.get(self.instance.departamento, [])
            city_choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]
            self.fields['ciudad'].choices = city_choices


class BuyerProfileForm(forms.ModelForm):
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_departamento_buyer',
            'onchange': 'updateCitiesBuyer()'
        }),
        label="Departamento",
        required=True
    )
    
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_ciudad_buyer'
        }),
        label="Ciudad/Municipio",
        required=True
    )

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