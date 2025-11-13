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
            'fecha_disponibilidad': 'Fecha aproximada de disponibilidad',
            'notas': 'Notas Adicionales'
        }
        
        help_texts = {
            'fecha_disponibilidad': 'Fecha estimada cuando el cultivo estará listo para cosechar. Obligatoria para todos los estados excepto "Cosechado".',
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Hacer todos los campos obligatorios excepto notas
        self.fields['nombre'].required = True
        self.fields['categoria'].required = True
        self.fields['cantidad_estimada'].required = True
        self.fields['unidad_medida'].required = True
        self.fields['area_ocupada'].required = True
        self.fields['estado'].required = True
        # notas permanece opcional (no se establece required)
        
        # Filtrar solo las fincas activas del usuario
        if user:
            farms = Farm.objects.filter(propietario=user, activa=True)
            self.fields['finca'].queryset = farms
            self.fields['finca'].empty_label = "Selecciona una finca"
            # Hacer el campo finca obligatorio
            self.fields['finca'].required = True
        else:
            self.fields['finca'].queryset = Farm.objects.none()
            self.fields['finca'].required = True
        
        # Hacer la fecha de disponibilidad obligatoria solo si el estado NO es "cosechado"
        estado = self.initial.get('estado') or (self.instance.estado if self.instance.pk else None)
        if estado != 'cosechado':
            self.fields['fecha_disponibilidad'].required = True
        else:
            self.fields['fecha_disponibilidad'].required = False
        
        # Agregar JavaScript para cambiar la obligatoriedad dinámicamente
        self.fields['estado'].widget.attrs['onchange'] = 'toggleFechaDisponibilidad()'
    
    def clean(self):
        cleaned_data = super().clean()
        finca = cleaned_data.get('finca')
        nombre = cleaned_data.get('nombre')
        categoria = cleaned_data.get('categoria')
        cantidad_estimada = cleaned_data.get('cantidad_estimada')
        unidad_medida = cleaned_data.get('unidad_medida')
        area_ocupada = cleaned_data.get('area_ocupada')
        estado = cleaned_data.get('estado')
        fecha_disponibilidad = cleaned_data.get('fecha_disponibilidad')
        user = getattr(self, 'user', None)
        
        errors = {}
        
        # Validar campos obligatorios
        if not finca:
            errors['finca'] = 'Este campo es obligatorio.'
        if not nombre:
            errors['nombre'] = 'Este campo es obligatorio.'
        if not categoria:
            errors['categoria'] = 'Este campo es obligatorio.'
        if cantidad_estimada is None or cantidad_estimada == 0:
            errors['cantidad_estimada'] = 'Este campo es obligatorio y debe ser mayor a 0.'
        if not unidad_medida:
            errors['unidad_medida'] = 'Este campo es obligatorio.'
        if area_ocupada is None:
            errors['area_ocupada'] = 'Este campo es obligatorio.'
        if not estado:
            errors['estado'] = 'Este campo es obligatorio.'
        
        # Validar que la fecha de disponibilidad sea obligatoria si el estado NO es "cosechado"
        if estado and estado != 'cosechado' and not fecha_disponibilidad:
            errors['fecha_disponibilidad'] = 'La fecha aproximada de disponibilidad es obligatoria para todos los estados excepto "Cosechado".'
        
        # Si se selecciona una finca, verificar que pertenezca al usuario
        if finca and user:
            if finca.propietario != user:
                errors['finca'] = "La finca seleccionada no pertenece al usuario actual."
            
            # Verificar que el área ocupada no exceda el área disponible
            if area_ocupada and finca.area_disponible < area_ocupada:
                errors['area_ocupada'] = (
                    f"El área ocupada ({area_ocupada} ha) excede el área disponible "
                    f"en la finca ({finca.area_disponible} ha)."
                )
        
        if errors:
            raise forms.ValidationError(errors)
        
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
            'fecha_disponibilidad': 'Fecha aproximada de disponibilidad',
            'notas': 'Notas Adicionales'
        }
        
        help_texts = {
            'fecha_disponibilidad': 'Fecha estimada cuando el cultivo estará listo para cosechar. Obligatoria para todos los estados excepto "Cosechado".',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hacer todos los campos obligatorios excepto notas
        self.fields['productor'].required = True
        self.fields['finca'].required = True
        self.fields['nombre'].required = True
        self.fields['categoria'].required = True
        self.fields['cantidad_estimada'].required = True
        self.fields['unidad_medida'].required = True
        self.fields['area_ocupada'].required = True
        self.fields['estado'].required = True
        # notas permanece opcional (no se establece required)
        
        # Filtrar solo usuarios que son productores
        producers = User.objects.filter(role='Productor', is_active=True)
        self.fields['productor'].queryset = producers
        self.fields['productor'].empty_label = "Selecciona un productor"
        
        # Inicialmente no hay fincas seleccionadas
        self.fields['finca'].queryset = Farm.objects.none()
        self.fields['finca'].empty_label = "Primero selecciona un productor"
        
        # Si estamos editando, cargar las fincas del productor actual
        if self.instance and self.instance.pk and self.instance.productor:
            farms = Farm.objects.filter(propietario=self.instance.productor, activa=True)
            self.fields['finca'].queryset = farms
        
        # Hacer la fecha de disponibilidad obligatoria solo si el estado NO es "cosechado"
        estado = self.initial.get('estado') or (self.instance.estado if self.instance.pk else None)
        if estado != 'cosechado':
            self.fields['fecha_disponibilidad'].required = True
        else:
            self.fields['fecha_disponibilidad'].required = False
        
        # Agregar JavaScript para cambiar la obligatoriedad dinámicamente
        self.fields['estado'].widget.attrs['onchange'] = 'toggleFechaDisponibilidad()'
    
    def clean(self):
        cleaned_data = super().clean()
        productor = cleaned_data.get('productor')
        finca = cleaned_data.get('finca')
        nombre = cleaned_data.get('nombre')
        categoria = cleaned_data.get('categoria')
        cantidad_estimada = cleaned_data.get('cantidad_estimada')
        unidad_medida = cleaned_data.get('unidad_medida')
        area_ocupada = cleaned_data.get('area_ocupada')
        estado = cleaned_data.get('estado')
        fecha_disponibilidad = cleaned_data.get('fecha_disponibilidad')
        
        errors = {}
        
        # Validar campos obligatorios
        if not productor:
            errors['productor'] = 'Este campo es obligatorio.'
        if not finca:
            errors['finca'] = 'Este campo es obligatorio.'
        if not nombre:
            errors['nombre'] = 'Este campo es obligatorio.'
        if not categoria:
            errors['categoria'] = 'Este campo es obligatorio.'
        if cantidad_estimada is None or cantidad_estimada == 0:
            errors['cantidad_estimada'] = 'Este campo es obligatorio y debe ser mayor a 0.'
        if not unidad_medida:
            errors['unidad_medida'] = 'Este campo es obligatorio.'
        if area_ocupada is None:
            errors['area_ocupada'] = 'Este campo es obligatorio.'
        if not estado:
            errors['estado'] = 'Este campo es obligatorio.'
        
        # Validar que la fecha de disponibilidad sea obligatoria si el estado NO es "cosechado"
        if estado and estado != 'cosechado' and not fecha_disponibilidad:
            errors['fecha_disponibilidad'] = 'La fecha aproximada de disponibilidad es obligatoria para todos los estados excepto "Cosechado".'
        
        # Verificar que la finca pertenezca al productor seleccionado
        if productor and finca:
            if finca.propietario != productor:
                errors['finca'] = "La finca seleccionada no pertenece al productor seleccionado."
            
            # Verificar que el área ocupada no exceda el área disponible
            if area_ocupada and finca.area_disponible < area_ocupada:
                errors['area_ocupada'] = (
                    f"El área ocupada ({area_ocupada} ha) excede el área disponible "
                    f"en la finca ({finca.area_disponible} ha)."
                )
        
        if errors:
            raise forms.ValidationError(errors)
        
        return cleaned_data
