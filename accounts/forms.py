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
    role = forms.ChoiceField(
        choices=User.ROLE_CHOICES,
        required=True,
        label="Tipo de Usuario",
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500'
        })
    )
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'data-cities-url': '/ajax/cities/'
        }),
        label="Departamento",
        required=True
    )
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
        }),
        label="Ciudad/Municipio",
        required=True
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'role', 'departamento', 'ciudad', 'password1', 'password2')
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
        fields = ('first_name', 'last_name', 'email', 'profile_image')
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
            'profile_image': 'Imagen de Perfil',
        }


class AdminUserEditForm(UserEditForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    is_active = forms.BooleanField(required=False, label="Activo")
    is_staff = forms.BooleanField(required=False, label="Staff (Admin)")

    class Meta(UserEditForm.Meta):
        fields = ('first_name', 'last_name', 'email', 'role', 'is_active', 'is_staff', 'profile_image')


class ProducerProfileForm(forms.ModelForm):
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'data-cities-url': '/ajax/cities/'  # Corrected URL
        }),
        label="Departamento",
        required=True
    )

    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
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


class BuyerProfileForm(forms.ModelForm):
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'id': 'id_departamento_buyer',
            'data-cities-url': '/ajax/cities/'  # Corrected URL
        }),
        label="Departamento",
        required=True
    )

    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
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