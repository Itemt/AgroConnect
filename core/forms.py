from django import forms
from .models import Farm
from .colombia_locations import get_departments, get_cities_by_department
from accounts.models import User

class FarmForm(forms.ModelForm):
    """Formulario para crear y editar fincas"""
    
    # Redefinir los campos problemáticos como ChoiceField
    departamento = forms.ChoiceField(
        choices=[('', 'Seleccionar departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
            'id': 'id_departamento'
        })
    )
    ciudad = forms.ChoiceField(
        choices=[('', 'Primero seleccione un departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white',
            'id': 'id_ciudad'
        })
    )
    
    class Meta:
        model = Farm
        fields = [
            'nombre', 'descripcion', 'departamento', 'ciudad', 'direccion',
            'coordenadas_lat', 'coordenadas_lng', 'area_total', 'area_cultivable',
            'tipo_suelo', 'tipo_riego', 'certificacion_organica', 'certificacion_bpa',
            'otras_certificaciones'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-400',
                'placeholder': 'Nombre de la finca'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-400',
                'rows': 3,
                'placeholder': 'Descripción de la finca'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-400',
                'rows': 2,
                'placeholder': 'Dirección completa de la finca'
            }),
            'coordenadas_lat': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-400',
                'step': '0.0000001',
                'placeholder': 'Latitud (opcional)'
            }),
            'coordenadas_lng': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-400',
                'step': '0.0000001',
                'placeholder': 'Longitud (opcional)'
            }),
            'area_total': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-400',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Área total en hectáreas'
            }),
            'area_cultivable': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-400',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Área cultivable en hectáreas'
            }),
            'tipo_suelo': forms.Select(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'tipo_riego': forms.Select(attrs={
                'class': 'block w-full px-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-success-500 focus:border-success-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white'
            }),
            'certificacion_organica': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'certificacion_bpa': forms.CheckboxInput(attrs={
                'class': 'form-checkbox'
            }),
            'otras_certificaciones': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Otras certificaciones (opcional)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar opciones de departamentos
        departments = get_departments()
        self.fields['departamento'].choices = [('', 'Seleccionar departamento')] + departments
        
        # Configurar ciudades basadas en el departamento seleccionado
        if self.data and 'departamento' in self.data:
            departamento = self.data.get('departamento')
            if departamento:
                ciudades = get_cities_by_department(departamento)
                self.fields['ciudad'].choices = [('', 'Seleccionar ciudad')] + ciudades
                self.fields['ciudad'].widget.attrs.pop('disabled', None)
        elif self.instance and self.instance.pk:
            departamento = self.instance.departamento
            if departamento:
                ciudades = get_cities_by_department(departamento)
                self.fields['ciudad'].choices = [('', 'Seleccionar ciudad')] + ciudades
        else:
            self.fields['ciudad'].choices = [('', 'Primero seleccione un departamento')]
            self.fields['ciudad'].widget.attrs['disabled'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        area_total = cleaned_data.get('area_total')
        area_cultivable = cleaned_data.get('area_cultivable')
        departamento = cleaned_data.get('departamento')
        ciudad = cleaned_data.get('ciudad')
        
        # Validar que si se selecciona una ciudad, también se haya seleccionado un departamento
        if ciudad and not departamento:
            raise forms.ValidationError(
                'Debe seleccionar un departamento antes de seleccionar una ciudad.'
            )
        
        # Validar que el área cultivable no sea mayor que el área total
        if area_total and area_cultivable:
            if area_cultivable > area_total:
                raise forms.ValidationError(
                    "El área cultivable no puede ser mayor que el área total de la finca."
                )
        
        return cleaned_data


class AdminFarmForm(forms.ModelForm):
    """Formulario para que los admins creen y editen fincas asociadas a cualquier productor"""
    
    # Campo para seleccionar el productor
    propietario = forms.ModelChoiceField(
        queryset=User.objects.filter(role='Productor', is_active=True),
        empty_label="Seleccionar productor",
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
            'id': 'id_propietario'
        })
    )
    
    # Redefinir los campos problemáticos como ChoiceField
    departamento = forms.ChoiceField(
        choices=[('', 'Seleccionar departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
            'id': 'id_departamento'
        })
    )
    ciudad = forms.ChoiceField(
        choices=[('', 'Primero seleccione un departamento')],
        widget=forms.Select(attrs={
            'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
            'id': 'id_ciudad'
        })
    )
    
    class Meta:
        model = Farm
        fields = [
            'propietario', 'nombre', 'descripcion', 'departamento', 'ciudad', 'direccion',
            'coordenadas_lat', 'coordenadas_lng', 'area_total', 'area_cultivable',
            'tipo_suelo', 'tipo_riego', 'certificacion_organica', 'certificacion_bpa',
            'otras_certificaciones', 'activa'
        ]
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
                'placeholder': 'Nombre de la finca'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
                'rows': 3,
                'placeholder': 'Descripción de la finca'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
                'rows': 2,
                'placeholder': 'Dirección completa de la finca'
            }),
            'coordenadas_lat': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
                'step': '0.0000001',
                'placeholder': 'Latitud (opcional)'
            }),
            'coordenadas_lng': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
                'step': '0.0000001',
                'placeholder': 'Longitud (opcional)'
            }),
            'area_total': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Área total en hectáreas'
            }),
            'area_cultivable': forms.NumberInput(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Área cultivable en hectáreas'
            }),
            'tipo_suelo': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white'
            }),
            'tipo_riego': forms.Select(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white'
            }),
            'certificacion_organica': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-brand-600 bg-gray-100 border-gray-300 rounded focus:ring-brand-500 dark:focus:ring-brand-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
            }),
            'certificacion_bpa': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-brand-600 bg-gray-100 border-gray-300 rounded focus:ring-brand-500 dark:focus:ring-brand-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
            }),
            'otras_certificaciones': forms.Textarea(attrs={
                'class': 'block w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-brand-500 focus:border-brand-500 dark:bg-gray-700 dark:text-white',
                'rows': 2,
                'placeholder': 'Otras certificaciones (opcional)'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'w-4 h-4 text-brand-600 bg-gray-100 border-gray-300 rounded focus:ring-brand-500 dark:focus:ring-brand-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Configurar opciones de departamentos
        departments = get_departments()
        self.fields['departamento'].choices = [('', 'Seleccionar departamento')] + departments
        
        # Configurar ciudades basadas en el departamento seleccionado
        if self.data and 'departamento' in self.data:
            departamento = self.data.get('departamento')
            if departamento:
                ciudades = get_cities_by_department(departamento)
                self.fields['ciudad'].choices = [('', 'Seleccionar ciudad')] + ciudades
                self.fields['ciudad'].widget.attrs.pop('disabled', None)
        elif self.instance and self.instance.pk:
            departamento = self.instance.departamento
            if departamento:
                ciudades = get_cities_by_department(departamento)
                self.fields['ciudad'].choices = [('', 'Seleccionar ciudad')] + ciudades
        else:
            self.fields['ciudad'].choices = [('', 'Primero seleccione un departamento')]
            self.fields['ciudad'].widget.attrs['disabled'] = True
    
    def clean(self):
        cleaned_data = super().clean()
        area_total = cleaned_data.get('area_total')
        area_cultivable = cleaned_data.get('area_cultivable')
        departamento = cleaned_data.get('departamento')
        ciudad = cleaned_data.get('ciudad')
        
        # Validar que si se selecciona una ciudad, también se haya seleccionado un departamento
        if ciudad and not departamento:
            raise forms.ValidationError(
                'Debe seleccionar un departamento antes de seleccionar una ciudad.'
            )
        
        # Validar que el área cultivable no sea mayor que el área total
        if area_total and area_cultivable:
            if area_cultivable > area_total:
                raise forms.ValidationError(
                    "El área cultivable no puede ser mayor que el área total de la finca."
                )
        
        return cleaned_data
