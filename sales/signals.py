from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Order
from core.models import create_notification
from payments.models import Payment


@receiver(post_save, sender=Order)
def order_status_notifications(sender, instance, created, **kwargs):
    """Envía notificaciones cuando cambia el estado de un pedido"""
    if created:
        # Nuevo pedido creado - notificar al vendedor
        create_notification(
            recipient=instance.vendedor,
            title='Nuevo pedido recibido',
            message=f'Has recibido un nuevo pedido #{instance.id} de {instance.comprador.first_name} {instance.comprador.last_name} por {instance.cantidad_acordada} {instance.publicacion.cultivo.unidad_medida} de {instance.publicacion.cultivo.nombre}.',
            category='order',
            order_id=instance.id,
        )
        
        # Notificar al comprador
        create_notification(
            recipient=instance.comprador,
            title='Pedido creado',
            message=f'Tu pedido #{instance.id} ha sido creado exitosamente. Esperando confirmación del vendedor.',
            category='order',
            order_id=instance.id,
        )
    else:
        # Estado del pedido cambió - enviar notificaciones según el estado
        if instance.estado == 'confirmado':
            # Pedido confirmado por el vendedor
            create_notification(
                recipient=instance.comprador,
                title='Pedido confirmado',
                message=f'Tu pedido #{instance.id} ha sido confirmado por el vendedor. El vendedor comenzará a preparar tu pedido.',
                category='order',
                order_id=instance.id,
            )
            
        elif instance.estado == 'en_preparacion':
            # Pedido en preparación
            create_notification(
                recipient=instance.comprador,
                title='Pedido en preparación',
                message=f'Tu pedido #{instance.id} está siendo preparado por el vendedor.',
                category='order',
                order_id=instance.id,
            )
            
        elif instance.estado == 'enviado':
            # Pedido enviado
            create_notification(
                recipient=instance.comprador,
                title='Pedido enviado',
                message=f'Tu pedido #{instance.id} ha sido enviado. Pronto lo recibirás.',
                category='order',
                order_id=instance.id,
            )
            
        elif instance.estado == 'en_transito':
            # Pedido en tránsito
            create_notification(
                recipient=instance.comprador,
                title='Pedido en tránsito',
                message=f'Tu pedido #{instance.id} está en camino hacia ti.',
                category='order',
                order_id=instance.id,
            )
            
        elif instance.estado == 'entregado':
            # Pedido entregado
            create_notification(
                recipient=instance.comprador,
                title='Pedido entregado',
                message=f'Tu pedido #{instance.id} ha sido entregado. Por favor confirma la recepción.',
                category='order',
                order_id=instance.id,
            )
            
        elif instance.estado == 'recibido':
            # Pedido recibido por el comprador
            create_notification(
                recipient=instance.vendedor,
                title='Pedido recibido',
                message=f'El comprador ha confirmado la recepción del pedido #{instance.id}.',
                category='order',
                order_id=instance.id,
            )
            
        elif instance.estado == 'completado':
            # Pedido completado
            create_notification(
                recipient=instance.comprador,
                title='Pedido completado',
                message=f'Tu pedido #{instance.id} ha sido completado exitosamente. ¡Gracias por tu compra!',
                category='order',
                order_id=instance.id,
            )
            
            create_notification(
                recipient=instance.vendedor,
                title='Pedido completado',
                message=f'El pedido #{instance.id} ha sido completado exitosamente. ¡Gracias por la venta!',
                category='order',
                order_id=instance.id,
            )
            
        elif instance.estado == 'cancelado':
            # Pedido cancelado
            create_notification(
                recipient=instance.comprador,
                title='Pedido cancelado',
                message=f'Tu pedido #{instance.id} ha sido cancelado.',
                category='order',
                order_id=instance.id,
            )
            
            create_notification(
                recipient=instance.vendedor,
                title='Pedido cancelado',
                message=f'El pedido #{instance.id} ha sido cancelado.',
                category='order',
                order_id=instance.id,
            )


@receiver(post_save, sender=Payment)
def payment_status_notifications(sender, instance, created, **kwargs):
    """Envía notificaciones cuando cambia el estado de un pago"""
    if created:
        # Nuevo pago creado
        create_notification(
            recipient=instance.user,
            title='Pago iniciado',
            message=f'Se ha iniciado el proceso de pago para el pedido #{instance.order.id}.',
            category='payment',
            order_id=instance.order.id,
            payment_id=instance.id,
        )
    else:
        # Estado del pago cambió
        if instance.status == 'approved':
            # Pago aprobado
            create_notification(
                recipient=instance.user,
                title='Pago aprobado',
                message=f'Tu pago del pedido #{instance.order.id} ha sido aprobado exitosamente.',
                category='payment',
                order_id=instance.order.id,
                payment_id=instance.id,
            )
            
            # Notificar al vendedor
            create_notification(
                recipient=instance.order.vendedor,
                title='Pago recibido',
                message=f'Has recibido el pago del pedido #{instance.order.id}. Puedes confirmar el pedido.',
                category='payment',
                order_id=instance.order.id,
                payment_id=instance.id,
            )
            
        elif instance.status == 'rejected':
            # Pago rechazado
            create_notification(
                recipient=instance.user,
                title='Pago rechazado',
                message=f'Tu pago del pedido #{instance.order.id} ha sido rechazado. Por favor, intenta nuevamente.',
                category='payment',
                order_id=instance.order.id,
                payment_id=instance.id,
            )
            
        elif instance.status == 'pending':
            # Pago pendiente
            create_notification(
                recipient=instance.user,
                title='Pago pendiente',
                message=f'Tu pago del pedido #{instance.order.id} está pendiente de procesamiento.',
                category='payment',
                order_id=instance.order.id,
                payment_id=instance.id,
            )