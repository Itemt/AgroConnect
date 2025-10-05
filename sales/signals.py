from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Sum, Count, Avg
from .models import Order
from accounts.models import ProducerProfile, BuyerProfile


@receiver(post_save, sender=Order)
def update_user_statistics(sender, instance, created, **kwargs):
    """
    Actualiza las estadísticas de ventas y compras cuando una orden cambia de estado
    """
    # Solo actualizar estadísticas si la orden está completada
    if instance.estado == 'completado':
        # Actualizar estadísticas del VENDEDOR (ProducerProfile)
        vendedor = instance.vendedor
        if vendedor and hasattr(vendedor, 'producer_profile'):
            producer_profile = vendedor.producer_profile
            
            # Obtener todas las órdenes completadas del vendedor
            completed_sales = Order.objects.filter(
                publicacion__cultivo__productor=vendedor,
                estado='completado'
            )
            
            # Actualizar total de ventas
            producer_profile.total_ventas = completed_sales.count()
            
            # Actualizar ingresos totales
            producer_profile.ingresos_totales = completed_sales.aggregate(
                total=Sum('precio_total')
            )['total'] or 0
            
            # Actualizar fecha de primera venta si no existe
            if not producer_profile.fecha_primera_venta and producer_profile.total_ventas > 0:
                primera_venta = completed_sales.order_by('created_at').first()
                if primera_venta:
                    producer_profile.fecha_primera_venta = primera_venta.created_at
            
            # Actualizar calificación promedio si hay ratings
            ratings = vendedor.calificaciones_recibidas.filter(tipo='comprador_a_vendedor')
            if ratings.exists():
                producer_profile.calificacion_promedio = ratings.aggregate(
                    avg=Avg('calificacion_general')
                )['avg'] or 0
                producer_profile.total_calificaciones = ratings.count()
            
            producer_profile.save()
        
        # Actualizar estadísticas del COMPRADOR (BuyerProfile)
        comprador = instance.comprador
        if comprador and hasattr(comprador, 'buyer_profile'):
            buyer_profile = comprador.buyer_profile
            
            # Obtener todas las órdenes completadas del comprador
            completed_purchases = Order.objects.filter(
                comprador=comprador,
                estado='completado'
            )
            
            # Actualizar total de compras
            buyer_profile.total_compras = completed_purchases.count()
            
            # Actualizar gastos totales
            buyer_profile.gastos_totales = completed_purchases.aggregate(
                total=Sum('precio_total')
            )['total'] or 0
            
            # Actualizar fecha de primera compra si no existe
            if not buyer_profile.fecha_primera_compra and buyer_profile.total_compras > 0:
                primera_compra = completed_purchases.order_by('created_at').first()
                if primera_compra:
                    buyer_profile.fecha_primera_compra = primera_compra.created_at
            
            buyer_profile.save()
    
    # Si la orden se cancela, también recalcular estadísticas
    elif instance.estado == 'cancelado':
        # En caso de cancelación, recalcular sin incluir esta orden
        # (Similar al código anterior pero excluyendo órdenes canceladas)
        pass
