from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import BaseModel
from marketplace.models import Publication

# Create your models here.

class Conversation(BaseModel):
    publication = models.ForeignKey(Publication, on_delete=models.CASCADE, related_name='conversations', null=True)
    participants = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='conversations')

    def __str__(self):
        return f"Conversation about {self.publication.pk if self.publication else 'N/A'}"

class Message(BaseModel):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages', null=True)
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sent_messages', null=True)
    content = models.TextField(default='')

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Message from {self.sender} in conversation {self.conversation.pk}"


class Order(BaseModel):
    ESTADO_CHOICES = (
        ('pendiente', 'Pendiente'),
        ('confirmado', 'Confirmado por Vendedor'),
        ('en_preparacion', 'En Preparación'),
        ('enviado', 'Enviado'),
        ('en_transito', 'En Tránsito'),
        ('entregado', 'Entregado'),
        ('recibido', 'Recibido por Comprador'),
        ('completado', 'Completado'),
        ('cancelado', 'Cancelado'),
    )
    
    # Relaciones
    publicacion = models.ForeignKey(Publication, on_delete=models.CASCADE, 
                                  related_name='pedidos', verbose_name="Publicación", null=True)
    comprador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                related_name='pedidos_como_comprador', verbose_name="Comprador", null=True)
    
    # Información del pedido
    cantidad_acordada = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          verbose_name="Cantidad Acordada")
    precio_total = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                     verbose_name="Precio Total")
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, 
                            default='pendiente', verbose_name="Estado del Pedido")
    
    # Información adicional
    notas_comprador = models.TextField(blank=True, null=True, 
                                     verbose_name="Notas del Comprador")
    notas_vendedor = models.TextField(blank=True, null=True, 
                                    verbose_name="Notas del Vendedor")
    direccion_entrega = models.TextField(verbose_name="Dirección de Entrega", blank=True)
    
    # Fechas de seguimiento
    fecha_confirmacion = models.DateTimeField(null=True, blank=True, 
                                            verbose_name="Fecha de Confirmación")
    fecha_envio = models.DateTimeField(null=True, blank=True, 
                                     verbose_name="Fecha de Envío")
    fecha_entrega_estimada = models.DateTimeField(null=True, blank=True, 
                                                verbose_name="Fecha de Entrega Estimada")
    fecha_recepcion = models.DateTimeField(null=True, blank=True, 
                                         verbose_name="Fecha de Recepción")

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ['-created_at']

    def __str__(self):
        return f'Pedido #{self.id} - {self.publicacion.cultivo.nombre_producto}'

    @property
    def vendedor(self):
        """Propiedad para obtener el vendedor del pedido"""
        return self.publicacion.cultivo.productor

    def can_be_confirmed_by_seller(self):
        """Verifica si el pedido puede ser confirmado por el vendedor"""
        return self.estado == 'pendiente'

    def can_be_marked_as_shipped(self):
        """Verifica si el pedido puede ser marcado como enviado"""
        return self.estado in ['confirmado', 'en_preparacion']

    def can_be_received_by_buyer(self):
        """Verifica si el pedido puede ser marcado como recibido por el comprador"""
        return self.estado in ['enviado', 'en_transito', 'entregado']

    def can_be_rated(self):
        """Verifica si el pedido puede ser calificado"""
        return self.estado == 'completado' and not hasattr(self, 'calificacion')

    def can_be_cancelled(self):
        """Verifica si el pedido puede ser cancelado"""
        return self.estado not in ['completado', 'cancelado', 'recibido']

    def can_be_cancelled_by_buyer(self):
        """Verifica si el comprador puede cancelar el pedido"""
        return self.estado in ['pendiente', 'confirmado'] and self.can_be_cancelled()

    def can_be_cancelled_by_seller(self):
        """Verifica si el vendedor puede cancelar el pedido"""
        return self.estado in ['pendiente', 'confirmado', 'en_preparacion'] and self.can_be_cancelled()

    def get_available_actions_for_user(self, user):
        """Obtiene las acciones disponibles para un usuario específico"""
        actions = []
        
        if user == self.comprador:
            # Acciones para el comprador
            if self.can_be_received_by_buyer():
                actions.append(('confirm_receipt', 'Confirmar Recepción', 'success'))
            if self.can_be_rated():
                actions.append(('rate', 'Calificar Vendedor', 'warning'))
            if self.can_be_cancelled_by_buyer():
                actions.append(('cancel', 'Cancelar Pedido', 'danger'))
                
        elif user == self.vendedor:
            # Acciones para el vendedor
            if self.can_be_confirmed_by_seller() or self.can_be_marked_as_shipped():
                actions.append(('update_status', 'Actualizar Estado', 'primary'))
            if self.can_be_cancelled_by_seller():
                actions.append(('cancel', 'Cancelar Pedido', 'danger'))
        
        # Acciones comunes
        actions.append(('contact', 'Contactar', 'outline'))
        
        return actions


class Rating(BaseModel):
    """Modelo para calificaciones de pedidos"""
    TIPO_CALIFICACION_CHOICES = (
        ('comprador_a_vendedor', 'Comprador califica a Vendedor'),
        ('vendedor_a_comprador', 'Vendedor califica a Comprador'),
    )
    
    pedido = models.OneToOneField(Order, on_delete=models.CASCADE, 
                                related_name='calificacion', verbose_name="Pedido", null=True)
    calificador = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                  related_name='calificaciones_dadas', verbose_name="Calificador", null=True)
    calificado = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                 related_name='calificaciones_recibidas', verbose_name="Calificado", null=True)
    
    tipo = models.CharField(max_length=25, choices=TIPO_CALIFICACION_CHOICES, default='comprador_a_vendedor',
                          verbose_name="Tipo de Calificación")
    
    # Calificaciones (1-5 estrellas)
    calificacion_general = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=0,
        verbose_name="Calificación General"
    )
    calificacion_comunicacion = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=0,
        verbose_name="Comunicación"
    )
    calificacion_puntualidad = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=0,
        verbose_name="Puntualidad"
    )
    calificacion_calidad = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], default=0,
        verbose_name="Calidad del Producto/Servicio"
    )
    
    # Comentarios
    comentario = models.TextField(blank=True, null=True, 
                                verbose_name="Comentario")
    
    # Recomendación
    recomendaria = models.BooleanField(default=True, 
                                     verbose_name="¿Recomendarías a este usuario?")

    class Meta:
        verbose_name = "Calificación"
        verbose_name_plural = "Calificaciones"
        ordering = ['-created_at']
        unique_together = ['pedido', 'calificador']  # Un usuario solo puede calificar una vez por pedido

    def __str__(self):
        return f'Calificación de {self.calificador.first_name} a {self.calificado.first_name} - Pedido #{self.pedido.id}'

    @property
    def promedio_calificacion(self):
        """Calcula el promedio de todas las calificaciones"""
        return (self.calificacion_general + self.calificacion_comunicacion + 
                self.calificacion_puntualidad + self.calificacion_calidad) / 4