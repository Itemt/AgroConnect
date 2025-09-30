from django import forms
from .models import Publication
from core.colombia_locations import get_all_cities

class PublicationForm(forms.ModelForm):
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona ubicación')] + get_all_cities(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False,
        label="Ubicación (Ciudad, Departamento)"
    )
    
    class Meta:
        model = Publication
        fields = [
            'cultivo', 'precio_por_unidad', 'cantidad_disponible', 'cantidad_minima',
            'ciudad', 'categoria', 'descripcion', 'imagen'
        ]
        widgets = {
            'cultivo': forms.Select(attrs={'class': 'form-control'}),
            'precio_por_unidad': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 2.50'}),
            'cantidad_disponible': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 100'}),
            'cantidad_minima': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Ej: 10'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['cultivo'].queryset = user.cultivos.all()
