from django import forms
from .models import Publication, PublicationImage
from core.colombia_locations import get_departments, COLOMBIA_LOCATIONS
from core.models import Farm
from inventory.models import Crop
from django.contrib.auth import get_user_model

User = get_user_model()


class MultipleImageInput(forms.ClearableFileInput):
    """Widget personalizado para permitir múltiples archivos"""
    allow_multiple_selected = True


class MultipleImageField(forms.ImageField):
    """Campo personalizado para manejar múltiples imágenes"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleImageInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result


class PublicationForm(forms.ModelForm):
    # Campo personalizado para múltiples imágenes
    images = MultipleImageField(
        required=False,
        label="Imágenes del Producto",
        help_text="Puedes subir hasta 10 imágenes. La primera será la imagen principal.",
        widget=MultipleImageInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100',
            'multiple': True,
            'accept': 'image/*'
        })
    )
    
    # Campos de ubicación solo para mostrar (no editables)
    departamento = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 cursor-not-allowed',
            'readonly': True
        }),
        label="Departamento de Origen",
        required=False
    )
    
    ciudad = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-xl bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 cursor-not-allowed',
            'readonly': True
        }),
        label="Ciudad/Municipio de Origen",
        required=False
    )
    
    class Meta:
        model = Publication
        fields = [
            'cultivo', 'finca', 'unidad_medida', 'precio_por_unidad', 'cantidad_disponible', 'cantidad_minima',
            'departamento', 'ciudad', 'categoria', 'descripcion'
        ]
        widgets = {
            'cultivo': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
            'finca': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white',
                'id': 'id_unidad_medida'
            }),
            'precio_por_unidad': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300', 
                'placeholder': 'Ej: 2.50'
            }),
            'cantidad_disponible': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300', 
                'placeholder': 'Ej: 100',
                'step': '0.01'
            }),
            'cantidad_minima': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300', 
                'placeholder': 'Ej: 10',
                'step': '0.01'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 resize-none', 
                'rows': 3
            })
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        crop = kwargs.pop('crop', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['cultivo'].queryset = user.cultivos.all()
            self.fields['finca'].queryset = Farm.objects.filter(propietario=user, activa=True)
            self.fields['finca'].empty_label = "Seleccionar finca (opcional)"
        
        # Si hay un cultivo específico (creación), establecer la ubicación automáticamente
        if crop and crop.finca:
            departamento_val = crop.finca.departamento or ''
            ciudad_val = crop.finca.ciudad or ''
            self.fields['departamento'].initial = departamento_val
            self.fields['departamento'].widget.attrs['value'] = departamento_val
            self.initial['departamento'] = departamento_val
            self.fields['ciudad'].initial = ciudad_val
            self.fields['ciudad'].widget.attrs['value'] = ciudad_val
            self.initial['ciudad'] = ciudad_val
            # Establecer el cultivo y finca automáticamente
            self.fields['cultivo'].initial = crop
            self.fields['finca'].initial = crop.finca
        
        # Si estamos editando (instance existe), establecer ubicación desde la publicación
        elif self.instance and self.instance.pk:
            if self.instance.cultivo and self.instance.cultivo.finca:
                departamento_val = self.instance.cultivo.finca.departamento or ''
                ciudad_val = self.instance.cultivo.finca.ciudad or ''
                self.fields['departamento'].initial = departamento_val
                self.fields['departamento'].widget.attrs['value'] = departamento_val
                self.initial['departamento'] = departamento_val
                self.fields['ciudad'].initial = ciudad_val
                self.fields['ciudad'].widget.attrs['value'] = ciudad_val
                self.initial['ciudad'] = ciudad_val
            # Si la publicación tiene su propia ubicación guardada, usarla
            elif self.instance.departamento and self.instance.ciudad:
                departamento_val = self.instance.departamento or ''
                ciudad_val = self.instance.ciudad or ''
                self.fields['departamento'].initial = departamento_val
                self.fields['departamento'].widget.attrs['value'] = departamento_val
                self.initial['departamento'] = departamento_val
                self.fields['ciudad'].initial = ciudad_val
                self.fields['ciudad'].widget.attrs['value'] = ciudad_val
                self.initial['ciudad'] = ciudad_val


class AdminPublicationForm(forms.ModelForm):
    """Formulario para que los admins creen publicaciones asociadas a cualquier productor"""
    
    # Campo personalizado para múltiples imágenes
    images = MultipleImageField(
        required=False,
        label="Imágenes del Producto",
        help_text="Puedes subir hasta 10 imágenes. La primera será la imagen principal.",
        widget=MultipleImageInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-brand-50 file:text-brand-700 hover:file:bg-brand-100',
            'multiple': True,
            'accept': 'image/*'
        })
    )
    
    # Campos de ubicación editables para admins
    departamento = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
            'placeholder': 'Ej: Cundinamarca'
        }),
        label="Departamento de Origen",
        required=True
    )
    
    ciudad = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
            'placeholder': 'Ej: Bogotá'
        }),
        label="Ciudad/Municipio de Origen",
        required=True
    )
    
    class Meta:
        model = Publication
        fields = [
            'cultivo', 'finca', 'unidad_medida', 'precio_por_unidad', 'cantidad_disponible', 'cantidad_minima',
            'departamento', 'ciudad', 'categoria', 'descripcion', 'estado'
        ]
        widgets = {
            'cultivo': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
                'id': 'id_cultivo'
            }),
            'finca': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
                'id': 'id_finca'
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white'
            }),
            'precio_por_unidad': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white', 
                'placeholder': 'Ej: 2.50',
                'step': '0.01',
                'min': '0'
            }),
            'cantidad_disponible': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white', 
                'placeholder': 'Ej: 100',
                'step': '0.01',
                'min': '0'
            }),
            'cantidad_minima': forms.NumberInput(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white', 
                'placeholder': 'Ej: 10',
                'step': '0.01',
                'min': '0'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white resize-none', 
                'rows': 4,
                'placeholder': 'Descripción detallada del producto, calidad, métodos de cultivo, etc.'
            })
        }
        labels = {
            'cultivo': 'Cultivo',
            'finca': 'Finca',
            'unidad_medida': 'Unidad de Medida',
            'precio_por_unidad': 'Precio por Unidad ($)',
            'cantidad_disponible': 'Cantidad Disponible',
            'cantidad_minima': 'Cantidad Mínima de Venta',
            'categoria': 'Categoría',
            'estado': 'Estado',
            'descripcion': 'Descripción Adicional'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Inicialmente no hay cultivos seleccionados
        self.fields['cultivo'].queryset = Crop.objects.none()
        self.fields['cultivo'].empty_label = "Primero selecciona un productor"
        self.fields['cultivo'].required = True
        
        # Inicialmente no hay fincas seleccionadas
        self.fields['finca'].queryset = Farm.objects.none()
        self.fields['finca'].empty_label = "Primero selecciona un productor"
        self.fields['finca'].required = False
        
        # Si estamos editando, cargar los cultivos y fincas del productor actual
        if self.instance and self.instance.pk and self.instance.cultivo:
            producer = self.instance.cultivo.productor
            crops = producer.cultivos.all()
            farms = Farm.objects.filter(propietario=producer, activa=True)
            
            self.fields['cultivo'].queryset = crops
            self.fields['finca'].queryset = farms
    
    def clean(self):
        cleaned_data = super().clean()
        cultivo = cleaned_data.get('cultivo')
        finca = cleaned_data.get('finca')
        cantidad_disponible = cleaned_data.get('cantidad_disponible')
        cantidad_minima = cleaned_data.get('cantidad_minima')
        
        # Verificar que la finca pertenezca al productor del cultivo
        if cultivo and finca:
            if finca.propietario != cultivo.productor:
                raise forms.ValidationError("La finca seleccionada no pertenece al productor del cultivo.")
        
        # Verificar que la cantidad mínima no sea mayor que la disponible
        if cantidad_disponible and cantidad_minima:
            if cantidad_minima > cantidad_disponible:
                raise forms.ValidationError("La cantidad mínima no puede ser mayor que la cantidad disponible.")
        
        return cleaned_data
