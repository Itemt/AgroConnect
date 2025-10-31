from django import forms
from .models import Crop
from core.models import Farm
from django.contrib.auth import get_user_model

User = get_user_model()

class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['finca', 'nombre', 'categoria', 'cantidad_estimada', 'unidad_medida', 'area_ocupada', 'estado', 'fecha_disponibilidad', 'notas']
        widgets = {
            'finca': forms.Select(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'placeholder': 'Ej: Tomate Chonto'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
            'cantidad_estimada': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'placeholder': '0'
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
            'area_ocupada': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'placeholder': '0'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
            'fecha_disponibilidad': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
            'notas': forms.Textarea(attrs={
                'rows': 6, 
                'placeholder': 'Información adicional sobre el cultivo, métodos de cultivo, calidad, etc.',
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
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
            self.fields['finca'].empty_label = "Selecciona una finca"
            # Hacer el campo finca obligatorio
            self.fields['finca'].required = True
        else:
            self.fields['finca'].queryset = Farm.objects.none()
    
    def clean(self):
        cleaned_data = super().clean()
        finca = cleaned_data.get('finca')
        area_ocupada = cleaned_data.get('area_ocupada')
        user = getattr(self, 'user', None)
        
        # Si se selecciona una finca, verificar que pertenezca al usuario
        if finca and user:
            if finca.propietario != user:
                raise forms.ValidationError("La finca seleccionada no pertenece al usuario actual.")
            
            # Verificar que el área ocupada no exceda el área disponible
            if area_ocupada and finca.area_disponible < area_ocupada:
                raise forms.ValidationError(
                    f"El área ocupada ({area_ocupada} ha) excede el área disponible "
                    f"en la finca ({finca.area_disponible} ha)."
                )
        
        return cleaned_data


class AdminCropForm(forms.ModelForm):
    """Formulario para que los admins creen cultivos asociados a cualquier productor"""
    
    class Meta:
        model = Crop
        fields = ['productor', 'finca', 'nombre', 'categoria', 'cantidad_estimada', 'unidad_medida', 'area_ocupada', 'estado', 'fecha_disponibilidad', 'notas']
        widgets = {
            'productor': forms.Select(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'id': 'id_productor'
            }),
            'finca': forms.Select(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'id': 'id_finca'
            }),
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'placeholder': 'Ej: Tomate Chonto'
            }),
            'categoria': forms.Select(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
            'cantidad_estimada': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'placeholder': 'Ej: 500'
            }),
            'unidad_medida': forms.Select(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
            'area_ocupada': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0',
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100',
                'placeholder': 'Ej: 0.5'
            }),
            'estado': forms.Select(attrs={
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
            'fecha_disponibilidad': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
            'notas': forms.Textarea(attrs={
                'rows': 6, 
                'placeholder': 'Información adicional sobre el cultivo, métodos de cultivo, calidad, etc.',
                'class': 'w-full px-5 py-4 text-base border-2 border-gray-300 dark:border-gray-600 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 dark:focus:ring-blue-400 dark:focus:border-blue-400 transition-all duration-300 resize-none bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100'
            }),
        }
        labels = {
            'productor': 'Productor',
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
        super().__init__(*args, **kwargs)
        
        # Filtrar solo usuarios que son productores
        producers = User.objects.filter(role='Productor', is_active=True)
        self.fields['productor'].queryset = producers
        self.fields['productor'].empty_label = "Selecciona un productor"
        self.fields['productor'].required = True
        
        # Inicialmente no hay fincas seleccionadas
        self.fields['finca'].queryset = Farm.objects.none()
        self.fields['finca'].empty_label = "Primero selecciona un productor"
        self.fields['finca'].required = True
        
        # Si estamos editando, cargar las fincas del productor actual
        if self.instance and self.instance.pk and self.instance.productor:
            farms = Farm.objects.filter(propietario=self.instance.productor, activa=True)
            self.fields['finca'].queryset = farms
    
    def clean(self):
        cleaned_data = super().clean()
        productor = cleaned_data.get('productor')
        finca = cleaned_data.get('finca')
        area_ocupada = cleaned_data.get('area_ocupada')
        
        # Verificar que la finca pertenezca al productor seleccionado
        if productor and finca:
            if finca.propietario != productor:
                raise forms.ValidationError("La finca seleccionada no pertenece al productor seleccionado.")
            
            # Verificar que el área ocupada no exceda el área disponible
            if area_ocupada and finca.area_disponible < area_ocupada:
                raise forms.ValidationError(
                    f"El área ocupada ({area_ocupada} ha) excede el área disponible "
                    f"en la finca ({finca.area_disponible} ha)."
                )
        
        return cleaned_data
