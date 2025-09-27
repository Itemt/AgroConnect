from django import forms
from .models import Publication

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['precio_por_unidad', 'cantidad_disponible', 'cantidad_minima', 'descripcion']
        widgets = {
            'descripcion': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Describe la calidad, características especiales del producto...'}),
            'precio_por_unidad': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'cantidad_disponible': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'cantidad_minima': forms.NumberInput(attrs={'step': '0.01', 'min': '0.01'}),
        }
