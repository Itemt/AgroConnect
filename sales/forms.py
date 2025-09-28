from django import forms
from .models import Message, Order, Rating

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4, 
                'placeholder': 'Escribe tu mensaje aquí...',
                'class': 'form-control'
            })
        }

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['cantidad_acordada', 'direccion_entrega', 'notas_comprador']
        widgets = {
            'cantidad_acordada': forms.NumberInput(attrs={
                'step': '0.01', 
                'min': '0.01',
                'class': 'form-control',
                'placeholder': 'Cantidad que deseas comprar'
            }),
            'direccion_entrega': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Dirección completa de entrega'
            }),
            'notas_comprador': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Notas adicionales para el vendedor (opcional)'
            })
        }
        labels = {
            'cantidad_acordada': 'Cantidad a Comprar',
            'direccion_entrega': 'Dirección de Entrega',
            'notas_comprador': 'Notas Adicionales'
        }

class OrderUpdateForm(forms.ModelForm):
    """Formulario para que el vendedor actualice el estado del pedido"""
    class Meta:
        model = Order
        fields = ['estado', 'notas_vendedor', 'fecha_entrega_estimada']
        widgets = {
            'estado': forms.Select(attrs={'class': 'form-control'}),
            'notas_vendedor': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Notas para el comprador sobre el estado del pedido'
            }),
            'fecha_entrega_estimada': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            })
        }
        labels = {
            'estado': 'Estado del Pedido',
            'notas_vendedor': 'Notas del Vendedor',
            'fecha_entrega_estimada': 'Fecha Estimada de Entrega'
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Limitar las opciones de estado según el rol y estado actual
        if self.instance and self.instance.pk:
            current_state = self.instance.estado
            
            if user and user.role == 'Productor':
                # Estados que puede cambiar un vendedor
                if current_state == 'pendiente':
                    choices = [
                        ('confirmado', 'Confirmar Pedido'),
                        ('cancelado', 'Cancelar Pedido')
                    ]
                elif current_state == 'confirmado':
                    choices = [
                        ('en_preparacion', 'En Preparación'),
                        ('cancelado', 'Cancelar Pedido')
                    ]
                elif current_state == 'en_preparacion':
                    choices = [
                        ('enviado', 'Marcar como Enviado'),
                    ]
                elif current_state == 'enviado':
                    choices = [
                        ('en_transito', 'En Tránsito'),
                        ('entregado', 'Entregado')
                    ]
                else:
                    choices = [(current_state, self.instance.get_estado_display())]
                
                self.fields['estado'].choices = choices

class RatingForm(forms.ModelForm):
    """Formulario para calificar un pedido"""
    class Meta:
        model = Rating
        fields = [
            'calificacion_general', 'calificacion_comunicacion', 
            'calificacion_puntualidad', 'calificacion_calidad',
            'comentario', 'recomendaria'
        ]
        widgets = {
            'calificacion_general': forms.Select(choices=[(i, f'{i} estrella{"s" if i > 1 else ""}') for i in range(1, 6)], attrs={'class': 'form-control'}),
            'calificacion_comunicacion': forms.Select(choices=[(i, f'{i} estrella{"s" if i > 1 else ""}') for i in range(1, 6)], attrs={'class': 'form-control'}),
            'calificacion_puntualidad': forms.Select(choices=[(i, f'{i} estrella{"s" if i > 1 else ""}') for i in range(1, 6)], attrs={'class': 'form-control'}),
            'calificacion_calidad': forms.Select(choices=[(i, f'{i} estrella{"s" if i > 1 else ""}') for i in range(1, 6)], attrs={'class': 'form-control'}),
            'comentario': forms.Textarea(attrs={
                'rows': 4,
                'class': 'form-control',
                'placeholder': 'Comparte tu experiencia con otros usuarios...'
            }),
            'recomendaria': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }
        labels = {
            'calificacion_general': 'Calificación General',
            'calificacion_comunicacion': 'Comunicación',
            'calificacion_puntualidad': 'Puntualidad',
            'calificacion_calidad': 'Calidad del Producto',
            'comentario': 'Comentario (opcional)',
            'recomendaria': '¿Recomendarías a este usuario?'
        }

class OrderConfirmReceiptForm(forms.Form):
    """Formulario simple para que el comprador confirme la recepción"""
    confirmar_recepcion = forms.BooleanField(
        required=True,
        label="Confirmo que he recibido el pedido en buen estado",
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    notas_recepcion = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Notas sobre la recepción del pedido (opcional)'
        }),
        label="Notas sobre la recepción"
    )

class OrderSearchForm(forms.Form):
    """Formulario para buscar y filtrar pedidos"""
    ESTADO_CHOICES = [('', 'Todos los estados')] + list(Order.ESTADO_CHOICES)
    
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Buscar por producto, comprador o vendedor...'
        }),
        label="Buscar"
    )
    estado = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label="Estado"
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label="Desde"
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control'
        }),
        label="Hasta"
    )