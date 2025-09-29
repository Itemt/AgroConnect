from django import forms
from .models import Crop, Product
from core.colombia_locations import get_departments, COLOMBIA_LOCATIONS

class CropForm(forms.ModelForm):
    # Campo de categoría simple
    categoria = forms.ChoiceField(
        choices=[('', 'Selecciona una categoría')] + list(Product.CATEGORIA_CHOICES),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Categoría del Producto",
        required=True
    )
    
    # Campos de ubicación
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_departamento_crop',
            'data-cities-url': '/ajax/cities/'  # Corrected URL
        }),
        label="Departamento",
        required=False,
        help_text="Opcional: Especifica la ubicación de este cultivo"
    )
    
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'form-control',
            'id': 'id_ciudad_crop'
        }),
        label="Ciudad/Municipio",
        required=False
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
                pass  # Handle cases where department is not valid
        elif self.instance.pk and hasattr(self.instance, 'departamento') and self.instance.departamento:
            # For existing instances, populate cities based on the saved department
            cities = COLOMBIA_LOCATIONS.get(self.instance.departamento, [])
            self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]
    
    class Meta:
        model = Crop
        fields = ['nombre_producto', 'categoria', 'departamento', 'ciudad', 'cantidad_estimada', 'unidad_medida', 'estado', 'fecha_disponibilidad', 'notas']
        widgets = {
            'nombre_producto': forms.TextInput(attrs={
                'placeholder': 'Ej: Tomate cherry, Lechuga crespa, Zanahoria orgánica...',
                'class': 'form-control'
            }),
            'cantidad_estimada': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'form-control',
                'placeholder': 'Ej: 500'
            }),
            'unidad_medida': forms.Select(attrs={'class': 'form-control'}),
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'fecha_disponibilidad': forms.DateInput(attrs={
                'type': 'date',
                'class': 'form-control'
            }),
            'notas': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Información adicional sobre el cultivo, métodos de cultivo, calidad, etc.',
                'class': 'form-control'
            }),
        }
