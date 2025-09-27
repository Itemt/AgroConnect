from django import forms
from .models import Crop

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['product', 'estimated_quantity', 'unit', 'status', 'estimated_availability_date']
        widgets = {
            'estimated_availability_date': forms.DateInput(attrs={'type': 'date'}),
        }
