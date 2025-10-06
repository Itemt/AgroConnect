from django import forms
from .models import Farm
from .colombia_locations import get_departments, get_cities_by_department

class FarmForm(forms.ModelForm):
    """Formulario para crear y editar fincas"""
    
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
                'class': 'form-input',
                'placeholder': 'Nombre de la finca'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 3,
                'placeholder': 'Descripción de la finca'
            }),
            'departamento': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_departamento'
            }),
            'ciudad': forms.Select(attrs={
                'class': 'form-select',
                'id': 'id_ciudad'
            }),
            'direccion': forms.Textarea(attrs={
                'class': 'form-input',
                'rows': 2,
                'placeholder': 'Dirección completa de la finca'
            }),
            'coordenadas_lat': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.0000001',
                'placeholder': 'Latitud (opcional)'
            }),
            'coordenadas_lng': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.0000001',
                'placeholder': 'Longitud (opcional)'
            }),
            'area_total': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Área total en hectáreas'
            }),
            'area_cultivable': forms.NumberInput(attrs={
                'class': 'form-input',
                'step': '0.01',
                'min': '0.01',
                'placeholder': 'Área cultivable en hectáreas'
            }),
            'tipo_suelo': forms.Select(attrs={
                'class': 'form-select'
            }),
            'tipo_riego': forms.Select(attrs={
                'class': 'form-select'
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
        self.fields['departamento'].choices = [('', 'Seleccionar departamento')] + get_departments()
        
        # Configurar opciones de ciudades basadas en el departamento seleccionado
        if self.instance and self.instance.pk:
            # Si estamos editando, cargar las ciudades del departamento actual
            departamento = self.instance.departamento
            if departamento:
                ciudades = get_cities_by_department(departamento)
                self.fields['ciudad'].choices = [('', 'Seleccionar ciudad')] + ciudades
            else:
                self.fields['ciudad'].choices = [('', 'Seleccionar ciudad')]
        else:
            # Si estamos creando, no hay ciudades disponibles hasta seleccionar departamento
            self.fields['ciudad'].choices = [('', 'Primero seleccione un departamento')]
    
    def clean(self):
        cleaned_data = super().clean()
        area_total = cleaned_data.get('area_total')
        area_cultivable = cleaned_data.get('area_cultivable')
        
        if area_total and area_cultivable:
            if area_cultivable > area_total:
                raise forms.ValidationError(
                    "El área cultivable no puede ser mayor que el área total de la finca."
                )
        
        return cleaned_data
