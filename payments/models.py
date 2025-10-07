from django.db import models
from django.conf import settings
from core.models import BaseModel
from sales.models import Order
from core.models import create_notification


class Payment(BaseModel):
    """Modelo para almacenar información de pagos con MercadoPago"""
    
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
        ('in_process', 'En Proceso'),
        ('in_mediation', 'En Mediación'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('pse', 'PSE'),
        ('credit_card', 'Tarjeta de Crédito'),
        ('debit_card', 'Tarjeta de Débito'),
        ('cash', 'Efectivo'),
        ('bank_transfer', 'Transferencia Bancaria'),
    )
    
    # Relaciones
    order = models.OneToOneField(
        Order, 
        on_delete=models.CASCADE, 
        related_name='payment',
        verbose_name="Pedido"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='payments',
        verbose_name="Usuario"
    )
    
    # Información de MercadoPago
    mercadopago_id = models.CharField(
        max_length=255, 
        unique=True,
        null=True,
        blank=True,
        verbose_name="ID MercadoPago",
        help_text="ID único de la transacción en MercadoPago"
    )
    preference_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="ID de Preferencia",
        help_text="ID de la preferencia de pago creada"
    )
    external_reference = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name="Referencia Externa",
        help_text="Referencia externa única del pago"
    )
    
    # Detalles del pago
    amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        verbose_name="Monto"
    )
    currency = models.CharField(
        max_length=3, 
        default='COP',
        verbose_name="Moneda"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES,
        verbose_name="Método de Pago"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Estado del Pago"
    )
    
    # Información adicional
    description = models.TextField(
        blank=True,
        verbose_name="Descripción"
    )
    response_data = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="Datos de Respuesta",
        help_text="Respuesta completa de MercadoPago"
    )
    
    # Fechas
    paid_at = models.DateTimeField(
        null=True, 
        blank=True,
        verbose_name="Fecha de Pago"
    )
    
    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ['-created_at']
    
    def __str__(self):
        return f'Pago {self.mercadopago_id} - {self.get_status_display()}'
    
    @property
    def is_approved(self):
        """Verifica si el pago fue aprobado"""
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        """Verifica si el pago está pendiente"""
        return self.status == 'pending'
    
    def mark_as_approved(self):
        """Marca el pago como aprobado - la orden permanece pendiente hasta que el vendedor la confirme"""
        from django.utils import timezone
        
        self.status = 'approved'
        self.paid_at = timezone.now()
        self.save()
        
        # La orden permanece en 'pendiente' hasta que el vendedor la confirme manualmente
        # Esto permite que el vendedor revise y acepte el pedido antes de empezar a prepararlo

        # Notificar al vendedor y al comprador
        create_notification(
            recipient=self.order.vendedor,
            title='Pago aprobado',
            message=f'El pago del pedido #{self.order.id} ha sido aprobado.',
            category='payment',
            order_id=self.order.id,
            payment_id=self.id,
        )
        create_notification(
            recipient=self.user,
            title='Pago confirmado',
            message=f'Tu pago del pedido #{self.order.id} fue aprobado.',
            category='payment',
            order_id=self.order.id,
            payment_id=self.id,
        )
    
    def mark_as_rejected(self):
        """Marca el pago como rechazado"""
        self.status = 'rejected'
        self.save()
        
        # Restaurar cantidad en la publicación
        publication = self.order.publicacion
        publication.cantidad_disponible += self.order.cantidad_acordada
        publication.save()
        
        # Cancelar la orden
        self.order.estado = 'cancelado'
        self.order.save()

        # Notificar al comprador y vendedor del rechazo
        create_notification(
            recipient=self.user,
            title='Pago rechazado',
            message=f'Tu pago del pedido #{self.order.id} fue rechazado.',
            category='payment',
            order_id=self.order.id,
            payment_id=self.id,
        )
        create_notification(
            recipient=self.order.vendedor,
            title='Pago rechazado',
            message=f'El pago del pedido #{self.order.id} fue rechazado y la orden se canceló.',
            category='payment',
            order_id=self.order.id,
            payment_id=self.id,
        )
