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
            'onchange': 'updateCitiesCrop()'
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
        
        # Si hay una instancia, configurar las ciudades para el departamento seleccionado
        if self.instance.pk and hasattr(self.instance, 'departamento') and self.instance.departamento:
            cities = COLOMBIA_LOCATIONS.get(self.instance.departamento, [])
            city_choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]
            self.fields['ciudad'].choices = city_choices
    
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
