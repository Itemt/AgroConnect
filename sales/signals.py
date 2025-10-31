from django.db.models.signals import post_save, pre_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Order, Rating
from core.models import create_notification, Notification
from payments.models import Payment
from accounts.models import ProducerProfile, BuyerProfile
from django.db.models import Avg


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


@receiver(post_save, sender=Order)
def update_seller_stats_on_completion(sender, instance, created, **kwargs):
    """Actualiza estadísticas del vendedor cuando se completa un pedido"""
    if not created and instance.estado == 'completado':
        try:
            # Obtener o crear perfil del vendedor
            seller_profile, created = ProducerProfile.objects.get_or_create(
                user=instance.vendedor,
                defaults={
                    'total_ventas': 0,
                    'ingresos_totales': 0,
                    'calificacion_promedio': 0,
                    'total_calificaciones': 0,
                }
            )
            
            # Actualizar estadísticas
            seller_profile.total_ventas += 1
            seller_profile.ingresos_totales += instance.precio_total
            
            # Establecer fecha de primera venta si es la primera
            if seller_profile.total_ventas == 1:
                seller_profile.fecha_primera_venta = timezone.now()
            
            seller_profile.save()
            
        except Exception as e:
            print(f"Error updating seller stats: {e}")


@receiver(post_save, sender=Order)
def update_buyer_stats_on_completion(sender, instance, created, **kwargs):
    """Actualiza estadísticas del comprador cuando se completa un pedido"""
    if not created and instance.estado == 'completado':
        try:
            # Obtener o crear perfil del comprador
            buyer_profile, created = BuyerProfile.objects.get_or_create(
                user=instance.comprador,
                defaults={
                    'total_compras': 0,
                    'gastos_totales': 0,
                }
            )
            
            # Actualizar estadísticas
            buyer_profile.total_compras += 1
            buyer_profile.gastos_totales += instance.precio_total
            buyer_profile.save()
            
        except Exception as e:
            print(f"Error updating buyer stats: {e}")


@receiver(post_save, sender=Rating)
def update_rating_stats(sender, instance, created, **kwargs):
    """Actualiza estadísticas de calificaciones cuando se crea una nueva calificación"""
    if created:
        try:
            if instance.tipo == 'comprador_a_vendedor':
                # Calificación de comprador a vendedor
                try:
                    seller_profile, _ = ProducerProfile.objects.get_or_create(
                        user=instance.calificado,
                        defaults={
                            'total_ventas': 0,
                            'ingresos_totales': 0,
                            'calificacion_promedio': 0,
                            'total_calificaciones': 0,
                        }
                    )
                    
                    # Recalcular promedio de calificaciones basado en calificado (más preciso)
                    ratings = Rating.objects.filter(
                        calificado=instance.calificado,
                        tipo='comprador_a_vendedor'
                    )
                    
                    if ratings.exists():
                        avg_rating = ratings.aggregate(avg=Avg('calificacion_general'))['avg']
                        seller_profile.calificacion_promedio = round(avg_rating, 1)  # Usar 1 decimal
                        seller_profile.total_calificaciones = ratings.count()
                        seller_profile.save()
                    else:
                        # Si no hay calificaciones, resetear a 0
                        seller_profile.calificacion_promedio = 0
                        seller_profile.total_calificaciones = 0
                        seller_profile.save()
                        
                except ProducerProfile.DoesNotExist:
                    # Si no existe el perfil, crearlo con valores por defecto
                    ProducerProfile.objects.create(
                        user=instance.calificado,
                        total_ventas=0,
                        ingresos_totales=0,
                        calificacion_promedio=0,
                        total_calificaciones=0,
                    )
                except Exception as e:
                    print(f"Error updating rating stats: {e}")
        except Exception as e:
            print(f"Error in update_rating_stats: {e}")


@receiver(pre_delete, sender=Order)
def delete_order_notifications(sender, instance, **kwargs):
    """Elimina todas las notificaciones relacionadas con un pedido cuando se borra"""
    try:
        # Eliminar notificaciones que referencian este pedido
        deleted_count = Notification.objects.filter(order_id=instance.id).count()
        Notification.objects.filter(order_id=instance.id).delete()
        print(f"Deleted {deleted_count} notifications for order {instance.id}")
    except Exception as e:
        print(f"Error deleting notifications for order {instance.id}: {e}")