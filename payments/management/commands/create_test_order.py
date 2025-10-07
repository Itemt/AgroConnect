"""
Comando para crear un pedido de prueba con monto válido para MercadoPago
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from sales.models import Order
from inventory.models import Publication
from accounts.models import ProducerProfile, BuyerProfile
from decimal import Decimal

User = get_user_model()

class Command(BaseCommand):
    help = 'Crea un pedido de prueba con monto válido para MercadoPago'

    def handle(self, *args, **options):
        # Buscar un usuario comprador
        buyer = User.objects.filter(buyer_profile__isnull=False).first()
        if not buyer:
            self.stdout.write(
                self.style.ERROR('No se encontró ningún usuario comprador')
            )
            return

        # Buscar una publicación
        publication = Publication.objects.filter(activa=True).first()
        if not publication:
            self.stdout.write(
                self.style.ERROR('No se encontró ninguna publicación activa')
            )
            return

        # Crear pedido con monto mínimo de $10,000 COP
        cantidad = 10  # 10 unidades
        precio_total = publication.precio_por_unidad * cantidad

        # Asegurar que el monto sea al menos $10,000
        if precio_total < 10000:
            cantidad = (10000 // publication.precio_por_unidad) + 1
            precio_total = publication.precio_por_unidad * cantidad

        order = Order.objects.create(
            comprador=buyer,
            vendedor=publication.productor.user,
            publicacion=publication,
            cantidad_acordada=cantidad,
            precio_total=precio_total,
            estado='pendiente',
            notas_comprador='Pedido de prueba para MercadoPago'
        )

        self.stdout.write(
            self.style.SUCCESS(
                f'✅ Pedido de prueba creado: #{order.id}\n'
                f'   Producto: {publication.cultivo.nombre}\n'
                f'   Cantidad: {cantidad} {publication.cultivo.unidad_medida}\n'
                f'   Precio unitario: ${publication.precio_por_unidad:,.0f} COP\n'
                f'   Total: ${precio_total:,.0f} COP\n'
                f'   Comprador: {buyer.get_full_name()}\n'
                f'   Vendedor: {publication.productor.user.get_full_name()}\n'
                f'   URL: https://agroconnect.itemt.tech/order/{order.id}/'
            )
        )
