from django import forms
from .models import Publication

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = ['price_per_unit', 'available_quantity']
        labels = {
            'price_per_unit': 'Precio por Unidad (ej. por kg)',
            'available_quantity': 'Cantidad Total Disponible para la Venta',
        }
