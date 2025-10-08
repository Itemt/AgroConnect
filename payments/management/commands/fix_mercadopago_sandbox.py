"""
Comando para arreglar problemas de sandbox de MercadoPago
"""
from django.core.management.base import BaseCommand
from payments.mercadopago_service import MercadoPagoService
from sales.models import Order
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Arreglar problemas de sandbox de MercadoPago'

    def handle(self, *args, **options):
        self.stdout.write('=== ARREGLANDO MERCADOPAGO SANDBOX ===')
        
        # Probar el servicio
        service = MercadoPagoService()
        self.stdout.write(f'Token: {service.access_token[:20]}...')
        self.stdout.write(f'Es sandbox: {service.access_token.startswith("TEST-")}')
        
        # Crear una preferencia de prueba
        try:
            # Buscar un pedido de prueba
            order = Order.objects.filter(estado='pendiente').first()
            if not order:
                self.stdout.write('ERROR: No hay pedidos pendientes para probar')
                return
            
            user = order.comprador
            self.stdout.write(f'Probando con pedido #{order.id} del usuario {user.username}')
            
            # Crear preferencia
            result = service.create_preference(order, user)
            
            if result['success']:
                self.stdout.write('SUCCESS: Preferencia creada correctamente')
                self.stdout.write(f'ID: {result["preference_id"]}')
                self.stdout.write(f'URL: {result["init_point"]}')
                
                # Verificar si la URL es de sandbox
                if 'sandbox' in result['init_point']:
                    self.stdout.write('INFO: URL es de sandbox - OK')
                else:
                    self.stdout.write('WARNING: URL no es de sandbox - puede causar problemas')
                    
            else:
                self.stdout.write(f'ERROR: {result["error"]}')
                
        except Exception as e:
            self.stdout.write(f'ERROR: {str(e)}')
        
        self.stdout.write('=====================================')
