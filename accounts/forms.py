from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User, ProducerProfile, BuyerProfile
from core.colombia_locations import get_departments, get_all_cities, COLOMBIA_LOCATIONS


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
    
    # Campos de vendedor (solo requeridos si can_sell=True)
    direccion = forms.CharField(
        max_length=255, 
        required=False, 
        label="Dirección de la Finca",
        widget=forms.TextInput(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500',
            'placeholder': 'Ej: Vereda La Esperanza, Finca Los Naranjos'
        })
    )
    farm_description = forms.CharField(
        required=False, 
        label="Descripción de la Finca",
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
        fields = ('username', 'first_name', 'last_name', 'email', 'cedula', 'can_sell', 'departamento', 'ciudad', 'direccion', 'farm_description', 'main_crops', 'password1', 'password2')
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Aplicar clases CSS a los campos de contraseña
        self.fields['password1'].widget.attrs.update({
            'class': 'form-input',
            'placeholder': 'Mínimo 6 caracteres'
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