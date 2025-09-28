from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ProducerProfile, BuyerProfile

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('role', 'first_name', 'last_name', 'email')
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
            'role': 'Rol',
        }

class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        labels = {
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'email': 'Correo Electrónico',
        }

class ProducerProfileForm(forms.ModelForm):
    class Meta:
        model = ProducerProfile
        fields = ['location', 'farm_description', 'main_crops']
        labels = {
            'location': 'Ubicación',
            'farm_description': 'Descripción de la granja',
            'main_crops': 'Cultivos principales',
        }

class BuyerProfileForm(forms.ModelForm):
    class Meta:
        model = BuyerProfile
        fields = ['company_name', 'business_type']
        labels = {
            'company_name': 'Nombre de la empresa',
            'business_type': 'Tipo de negocio',
        }
