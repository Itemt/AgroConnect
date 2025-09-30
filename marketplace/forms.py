from django import forms
from .models import Publication

class PublicationForm(forms.ModelForm):
    class Meta:
        model = Publication
        fields = [
            'cultivo', 'precio_por_unidad', 'cantidad_disponible', 'cantidad_minima',
            'departamento', 'ciudad', 'categoria', 'descripcion', 'imagen'
        ]
        widgets = {
            'cultivo': forms.Select(attrs={'class': 'form-control'}),
            'precio_por_unidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2.50'}),
            'cantidad_disponible': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 100'}),
            'cantidad_minima': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10'}),
            'departamento': forms.Select(attrs={'class': 'form-control'}),
            'ciudad': forms.Select(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['cultivo'].queryset = user.cultivos.all()
