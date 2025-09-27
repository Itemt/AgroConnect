from django import forms
from .models import Message, Order

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Escribe tu mensaje aquí...'}),
        }
        labels = {
            'content': '',
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['cantidad_acordada', 'direccion_entrega', 'notas_comprador']
        widgets = {
            'cantidad_acordada': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0.01',
                'class': 'form-control'
            }),
            'direccion_entrega': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Ingresa tu dirección completa de entrega...',
                'class': 'form-control'
            }),
            'notas_comprador': forms.Textarea(attrs={
                'rows': 2,
                'placeholder': 'Comentarios adicionales, preferencias, etc. (opcional)',
                'class': 'form-control'
            }),
        }
