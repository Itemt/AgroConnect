from django import forms
from .models import Crop

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['nombre', 'categoria', 'cantidad_estimada', 'unidad_medida', 'estado', 'fecha_disponibilidad', 'notas', 'imagen']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: Tomate Chonto'
            }),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
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
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
