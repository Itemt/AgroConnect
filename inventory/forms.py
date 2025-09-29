from django import forms
from .models import Crop, Product

class CropForm(forms.ModelForm):
    producto = forms.ModelChoiceField(
        queryset=Product.objects.all().order_by('nombre'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Tipo de Producto",
        empty_label="Selecciona un producto"
    )

    class Meta:
        model = Crop
        fields = ['producto', 'cantidad_estimada', 'unidad_medida', 'estado', 'fecha_disponibilidad', 'notas']
        widgets = {
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
