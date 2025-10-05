from django import forms
from .models import Farm
from core.colombia_locations import get_departments, get_cities_by_department

class FarmForm(forms.ModelForm):
    """Formulario para crear y editar fincas"""
    
    class Meta:
        model = Farm
        fields = ['nombre', 'departamento', 'ciudad', 'direccion', 'descripcion', 'area', 'cultivos_principales', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Ej: Finca El Roble'
            }),
            'departamento': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white',
                'id': 'id_farm_departamento'
            }),
            'ciudad': forms.Select(attrs={
                'class': 'w-full px-4 py-3 pr-10 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 appearance-none bg-white',
                'id': 'id_farm_ciudad'
            }),
            'direccion': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Vereda, sector o dirección específica'
            }),
            'descripcion': forms.Textarea(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300 resize-none',
                'rows': 3,
                'placeholder': 'Descripción de la finca, tipo de terreno, clima, etc.'
            }),
            'area': forms.NumberInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'step': '0.01',
                'min': '0',
                'placeholder': 'Ej: 5.50'
            }),
            'cultivos_principales': forms.TextInput(attrs={
                'class': 'w-full px-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-primary-500 focus:border-primary-500 transition-all duration-300',
                'placeholder': 'Ej: Café, Plátano, Yuca'
            }),
            'activa': forms.CheckboxInput(attrs={
                'class': 'h-5 w-5 text-primary-600 border-gray-300 rounded focus:ring-primary-500 focus:ring-2 cursor-pointer'
            })
        }
        labels = {
            'nombre': 'Nombre de la Finca',
            'departamento': 'Departamento',
            'ciudad': 'Ciudad/Municipio',
            'direccion': 'Dirección/Vereda',
            'descripcion': 'Descripción',
            'area': 'Área (hectáreas)',
            'cultivos_principales': 'Cultivos Principales',
            'activa': 'Finca Activa'
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Cargar departamentos
        departments = get_departments()
        self.fields['departamento'].choices = [('', 'Selecciona un departamento')] + [(dept, dept) for dept in departments]
        
        # Si hay una instancia, cargar las ciudades del departamento seleccionado
        if self.instance and self.instance.pk and self.instance.departamento:
            cities = get_cities_by_department(self.instance.departamento)
            self.fields['ciudad'].choices = [('', 'Selecciona una ciudad')] + [(city, city) for city in cities]
        else:
            self.fields['ciudad'].choices = [('', 'Primero selecciona un departamento')]
