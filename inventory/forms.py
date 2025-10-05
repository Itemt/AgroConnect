from django import forms
from .models import Crop
from accounts.models import Farm

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['finca', 'nombre', 'categoria', 'cantidad_estimada', 'unidad_medida', 'estado', 'fecha_disponibilidad', 'notas']
        widgets = {
            'finca': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white'
            }),
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
        }
        labels = {
            'finca': 'Finca',
            'nombre': 'Nombre del Cultivo',
            'categoria': 'Categoría',
            'cantidad_estimada': 'Cantidad Estimada',
            'unidad_medida': 'Unidad de Medida',
            'estado': 'Estado del Cultivo',
            'fecha_disponibilidad': 'Fecha de Disponibilidad',
            'notas': 'Notas Adicionales'
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Filtrar solo las fincas activas del usuario
        if user:
            self.fields['finca'].queryset = Farm.objects.filter(user=user, activa=True)
            self.fields['finca'].empty_label = "Selecciona una finca (opcional)"
        else:
            self.fields['finca'].queryset = Farm.objects.none()
