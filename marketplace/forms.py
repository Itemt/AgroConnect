from django import forms
from .models import Publication
from core.colombia_locations import get_departments, COLOMBIA_LOCATIONS

class PublicationForm(forms.ModelForm):
    departamento = forms.ChoiceField(
        choices=[('', 'Selecciona un departamento')] + get_departments(),
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white',
            'data-cities-url': '/ajax/cities/'
        }),
        label="Departamento de Origen",
        required=False
    )
    
    ciudad = forms.ChoiceField(
        choices=[('', 'Selecciona primero un departamento')],
        widget=forms.Select(attrs={
            'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
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
            'cultivo': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
            'precio_por_unidad': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300', 
                'placeholder': 'Ej: 2.50'
            }),
            'cantidad_disponible': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300', 
                'placeholder': 'Ej: 100'
            }),
            'cantidad_minima': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300', 
                'placeholder': 'Ej: 10'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 resize-none', 
                'rows': 3
            }),
            'imagen': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100'
            }),
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
