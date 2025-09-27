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
        fields = ['agreed_quantity']
        labels = {
            'agreed_quantity': 'Cantidad que deseas comprar',
        }
