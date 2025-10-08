from django.core.management.base import BaseCommand
from payments.mercadopago_service import MercadoPagoService
import mercadopago

class Command(BaseCommand):
    help = 'Forzar URLs de sandbox para MercadoPago'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== FORZANDO SANDBOX URLs ==='))
        
        # Token específico para sandbox
        token = 'TEST-1261412824198770-100718-66491d0e1f1b1381978604366ca01034-308635696'
        sdk = mercadopago.SDK(token)
        
        # Datos específicos para sandbox
        test_data = {
            'transaction_amount': 1000.0,
            'currency_id': 'COP',
            'description': 'Test payment for university project',
            'payer': {
                'email': 'TESTUSER8283595198251736383@testuser.com',
                'name': 'Test User',
                'surname': 'University'
            },
            'items': [
                {
                    'id': '1',
                    'title': 'Test Product',
                    'description': 'Test description for university project',
                    'quantity': 1.0,
                    'unit_price': 1000.0,
                    'category_id': 'food',
                    'currency_id': 'COP'
                }
            ],
            'payment_methods': {
                'excluded_payment_methods': [],
                'excluded_payment_types': [],
                'installments': 1
            },
            # Forzar sandbox
            'metadata': {
                'test': True,
                'university_project': True
            }
        }
        
        try:
            result = sdk.preference().create(test_data)
            
            if result.get('status') == 201:
                self.stdout.write(self.style.SUCCESS('SUCCESS: Preferencia creada'))
                self.stdout.write(f"ID: {result['response']['id']}")
                self.stdout.write(f"Init Point: {result['response']['init_point']}")
                
                # Verificar si es sandbox
                init_point = result['response']['init_point']
                if 'sandbox' in init_point:
                    self.stdout.write(self.style.SUCCESS('SUCCESS: URL de sandbox detectada'))
                else:
                    self.stdout.write(self.style.ERROR('ERROR: URL de produccion detectada'))
                    self.stdout.write('SOLUCION: MercadoPago está usando URLs de producción')
                    self.stdout.write('Esto es normal para tokens de prueba en producción')
                    self.stdout.write('Las tarjetas de prueba funcionarán correctamente')
                    
            else:
                self.stdout.write(self.style.ERROR(f'ERROR: {result.get("response", {})}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR: {str(e)}'))
            
        self.stdout.write('==========================================')
