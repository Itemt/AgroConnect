from django import forms
from .models import Crop
from core.models import Farm

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['finca', 'nombre', 'categoria', 'cantidad_estimada', 'unidad_medida', 'area_ocupada', 'estado', 'fecha_disponibilidad', 'notas']
        widgets = {
            'finca': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Ej: Tomate Chonto'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
            'cantidad_estimada': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Ej: 500'
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
            'area_ocupada': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Ej: 0.5'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
            'fecha_disponibilidad': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300'
            }),
            'notas': forms.Textarea(attrs={
                'rows': 3, 
                'placeholder': 'Información adicional sobre el cultivo, métodos de cultivo, calidad, etc.',
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 resize-none'
            }),
        }
        labels = {
            'finca': 'Finca',
            'nombre': 'Nombre del Cultivo',
            'categoria': 'Categoría',
            'cantidad_estimada': 'Cantidad Estimada',
            'unidad_medida': 'Unidad de Medida',
            'area_ocupada': 'Área Ocupada (hectáreas)',
            'estado': 'Estado del Cultivo',
            'fecha_disponibilidad': 'Fecha de Disponibilidad',
            'notas': 'Notas Adicionales'
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar solo las fincas activas del usuario
        if user:
            farms = Farm.objects.filter(propietario=user, activa=True)
            self.fields['finca'].queryset = farms
            self.fields['finca'].empty_label = "Selecciona una finca (opcional)"
            # Hacer el campo finca opcional
            self.fields['finca'].required = False
        else:
            self.fields['finca'].queryset = Farm.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        finca = cleaned_data.get('finca')
        user = getattr(self, 'user', None)
        
        # Si se selecciona una finca, verificar que pertenezca al usuario
        if finca and user:
            if finca.propietario != user:
                raise forms.ValidationError("La finca seleccionada no pertenece al usuario actual.")
        
        return cleaned_data
