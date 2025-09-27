from django.db import models
from django.conf import settings
from core.models import BaseModel
from marketplace.models import Publication

# Create your models here.

class Conversation(BaseModel):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='conversations')
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')

    def __str__(self):
        return f"Conversation about {self.publication.pk}"

class Message(BaseModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages')
    content = models.TextField()

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender} in conversation {self.conversation.pk}"


class Order(BaseModel):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado'),
        ('en_preparacion', 'En Preparación'),
        ('en_transito', 'En Tránsito'),
        ('entregado', 'Entregado'),
        ('cancelado', 'Cancelado'),
    )
    
    # Relaciones
    publicacion = models.ForeignKey(Publication, on_delete=models.CASCADE, 
                                  related_name='pedidos', verbose_name="Publicación")
    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                related_name='pedidos_como_comprador', verbose_name="Comprador")
    
    # Información del pedido
    cantidad_acordada = models.DecimalField(max_digits=10, decimal_places=2, 
                                          verbose_name="Cantidad Acordada")
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, 
                                     verbose_name="Precio Total")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, 
                            default='pendiente', verbose_name="Estado del Pedido")
    
    # Información adicional
    notas_comprador = models.TextField(blank=True, null=True, 
                                     verbose_name="Notas del Comprador")
    direccion_entrega = models.TextField(verbose_name="Dirección de Entrega")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.id} - {self.publicacion.cultivo.nombre_producto}'
