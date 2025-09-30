from django import forms
from .models import Publication
from core.colombia_locations import get_departments, COLOMBIA_LOCATIONS

class PublicationForm(forms.ModelForm):
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'form-control',
            'data-cities-url': '/ajax/cities/'
        }),
        label="Departamento de Origen",
        required=False
    )
    
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label="Ciudad/Municipio de Origen",
        required=False
    )
    
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
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'imagen': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            self.fields['cultivo'].queryset = user.cultivos.all()
        
        # Cargar ciudades dinámicamente según el departamento seleccionado
        if 'departamento' in self.data:
            try:
                departamento = self.data.get('departamento')
                cities = COLOMBIA_LOCATIONS.get(departamento, [])
                self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]
            except (ValueError, TypeError):
                pass
        elif self.instance.pk and self.instance.departamento:
            # Para instancias existentes, poblar ciudades basadas en el departamento guardado
            cities = COLOMBIA_LOCATIONS.get(self.instance.departamento, [])
            self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in sorted(cities)]
