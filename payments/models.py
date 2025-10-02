from django.db import models
from django.conf import settings
from core.models import BaseModel
from sales.models import Order


class Payment(BaseModel):
    """Modelo para almacenar información de pagos con ePayco"""
    
    STATUS_CHOICES = (
        ('pending', 'Pendiente'),
        ('approved', 'Aprobado'),
        ('rejected', 'Rechazado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    )
    
    PAYMENT_METHOD_CHOICES = (
        ('card', 'Tarjeta de Crédito/Débito'),
        ('pse', 'PSE'),
        ('cash', 'Efectivo'),
        ('transfer', 'Transferencia'),
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
    
    # Información de ePayco
    epayco_ref = models.CharField(
        max_length=255, 
        unique=True, 
        verbose_name="Referencia ePayco",
        help_text="Referencia única de la transacción en ePayco"
    )
    epayco_transaction_id = models.CharField(
        max_length=255, 
        blank=True, 
        null=True,
        verbose_name="ID de Transacción ePayco"
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
        help_text="Respuesta completa de ePayco"
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
        return f'Pago {self.epayco_ref} - {self.get_status_display()}'
    
    @property
    def is_approved(self):
        """Verifica si el pago fue aprobado"""
        return self.status == 'approved'
    
    @property
    def is_pending(self):
        """Verifica si el pago está pendiente"""
        return self.status == 'pending'
    
    def mark_as_approved(self):
        """Marca el pago como aprobado y actualiza la orden"""
        from django.utils import timezone
        
        self.status = 'approved'
        self.paid_at = timezone.now()
        self.save()
        
        # Actualizar el estado de la orden
        if self.order.estado == 'pendiente':
            self.order.estado = 'confirmado'
            self.order.save()
    
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
