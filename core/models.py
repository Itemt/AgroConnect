from django.db import models
from django.conf import settings

# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Notification(BaseModel):
    CATEGORY_CHOICES = (
        ('order', 'Pedido'),
        ('payment', 'Pago'),
        ('system', 'Sistema'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinatario'
    )
    title = models.CharField(max_length=255, verbose_name='Título')
    message = models.TextField(verbose_name='Mensaje')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='system', verbose_name='Categoría')
    is_read = models.BooleanField(default=False, verbose_name='Leída')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Leída el')

    # Referencias opcionales
    order_id = models.IntegerField(null=True, blank=True, verbose_name='ID Pedido')
    payment_id = models.IntegerField(null=True, blank=True, verbose_name='ID Pago')

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} -> {self.recipient}"


# Helper to create and emit notifications via Channels
def create_and_emit_notification(*, recipient, title, message, category='system', order_id=None, payment_id=None):
    from asgiref.sync import async_to_sync
    from channels.layers import get_channel_layer
    from django.utils import timezone

    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        category=category,
        order_id=order_id,
        payment_id=payment_id,
    )

    channel_layer = get_channel_layer()
    group_name = f'user_{recipient.id}_notifications'
    payload = {
        'type': 'notification_message',
        'title': title,
        'message': message,
        'category': category,
        'order_id': order_id,
        'payment_id': payment_id,
        'created_at': timezone.localtime(notification.created_at).isoformat(),
    }
    async_to_sync(channel_layer.group_send)(group_name, payload)

    return notification
