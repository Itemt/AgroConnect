from django.db import models
from django.conf import settings
from core.models import BaseModel
from sales.models import Order
from core.models import create_notification
from core.email_service import email_service


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
        
        # Actualizar la cantidad disponible en la publicación (restar lo vendido)
        # Esto se hace DESPUÉS del pago para asegurar que solo se descuente cuando el pago está confirmado
        try:
            publication = self.order.publicacion
            # Verificar que hay suficiente cantidad disponible antes de restar
            if float(publication.cantidad_disponible) >= float(self.order.cantidad_acordada):
                publication.cantidad_disponible = float(publication.cantidad_disponible) - float(self.order.cantidad_acordada)
                publication.save()
            else:
                # Si no hay suficiente cantidad, registrar un error pero no fallar el pago
                import logging
                logger = logging.getLogger(__name__)
                logger.warning(
                    f"Pago aprobado pero cantidad insuficiente en publicación {publication.id}. "
                    f"Disponible: {publication.cantidad_disponible}, Solicitado: {self.order.cantidad_acordada}"
                )
        except Exception as e:
            # Evitar que un error en la actualización de cantidad afecte el flujo de pago
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error al actualizar cantidad disponible después del pago: {str(e)}")
        
        # La orden permanece en 'pendiente' hasta que el vendedor la confirme manualmente
        # Esto permite que el vendedor revise y acepte el pedido antes de empezar a prepararlo
        # Las notificaciones se manejan automáticamente a través de signals

        # Enviar recibo por email al comprador (post-pago)
        try:
            buyer_email = self.user.email
            buyer_name = getattr(self.user, 'first_name', None) or self.user.username
            email_service.send_order_confirmation_email(
                buyer_email,
                self.order,
                user_name=buyer_name,
            )
        except Exception:
            # Evitar que un error de correo afecte el flujo de pago
            pass

        # Notificar al vendedor
        try:
            seller = self.order.vendedor
            if seller and getattr(seller, 'email', None):
                seller_name = getattr(seller, 'first_name', None) or seller.username
                email_service.send_order_paid_seller_email(
                    seller.email,
                    self.order,
                    seller_name=seller_name,
                )
        except Exception:
            pass
    
    def mark_as_rejected(self):
        """Marca el pago como rechazado"""
        self.status = 'rejected'
        self.save()
        
        # Si el pago fue aprobado previamente y luego rechazado, restaurar la cantidad
        # (aunque esto no debería pasar normalmente, es una medida de seguridad)
        if self.paid_at:
            try:
                publication = self.order.publicacion
                publication.cantidad_disponible = float(publication.cantidad_disponible) + float(self.order.cantidad_acordada)
                publication.save()
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error al restaurar cantidad después de rechazar pago: {str(e)}")
        
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
