from django import forms
from .models import Publication
from core.colombia_locations import get_departments, COLOMBIA_LOCATIONS
from core.models import Farm

class PublicationForm(forms.ModelForm):
    # Campos de ubicación solo para mostrar (no editables)
    departamento = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-100 text-gray-600 cursor-not-allowed',
            'readonly': True
        }),
        label="Departamento de Origen",
        required=False
    )
    
    ciudad = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl bg-gray-100 text-gray-600 cursor-not-allowed',
            'readonly': True
        }),
        label="Ciudad/Municipio de Origen",
        required=False
    )
    
    class Meta:
        model = Publication
        fields = [
            'cultivo', 'finca', 'precio_por_unidad', 'cantidad_disponible', 'cantidad_minima',
            'departamento', 'ciudad', 'categoria', 'descripcion', 'imagen'
        ]
        widgets = {
            'cultivo': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
            'finca': forms.Select(attrs={
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
        crop = kwargs.pop('crop', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['cultivo'].queryset = user.cultivos.all()
            self.fields['finca'].queryset = Farm.objects.filter(propietario=user, activa=True)
            self.fields['finca'].empty_label = "Seleccionar finca (opcional)"
        
        # Si hay un cultivo específico, establecer la ubicación automáticamente
        if crop and crop.finca:
            self.fields['departamento'].initial = crop.finca.departamento
            self.fields['ciudad'].initial = crop.finca.ciudad
            # Establecer el cultivo y finca automáticamente
            self.fields['cultivo'].initial = crop
            self.fields['finca'].initial = crop.finca
