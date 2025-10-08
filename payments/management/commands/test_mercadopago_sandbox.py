from django.core.management.base import BaseCommand
from payments.mercadopago_service import MercadoPagoService
from payments.models import Payment
from django.contrib.auth import get_user_model
from sales.models import Order
from django.utils import timezone

User = get_user_model()

class Command(BaseCommand):
    help = 'Prueba MercadoPago Sandbox con datos específicos para proyecto universitario'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('=== PROBANDO MERCADOPAGO SANDBOX ==='))
        
        mercadopago_service = MercadoPagoService()
        self.stdout.write(f"Token: {mercadopago_service.access_token[:20]}...")
        self.stdout.write(f"Es sandbox: {mercadopago_service.access_token.startswith('TEST-')}")

        try:
            # Crear datos de prueba específicos para sandbox
            test_data = {
                'transaction_amount': 1000.0,
                'currency_id': 'COP',
                'description': 'Test payment for university project',
                'payer': {
                    'email': 'TESTUSER8283595198251736383@testuser.com',  # Cuenta comprador específica
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
                }
            }
            
            # Probar crear preferencia
            result = mercadopago_service.sdk.preference().create(test_data)
            
            if result.get('status') == 201:
                self.stdout.write(self.style.SUCCESS('SUCCESS: Preferencia creada exitosamente'))
                self.stdout.write(f"ID: {result['response']['id']}")
                self.stdout.write(f"Init Point: {result['response']['init_point']}")
                self.stdout.write(f"Es sandbox URL: {'sandbox' in result['response']['init_point']}")
                
                # Verificar si es sandbox
                if 'sandbox' in result['response']['init_point']:
                    self.stdout.write(self.style.SUCCESS('SUCCESS: URL de sandbox detectada'))
                else:
                    self.stdout.write(self.style.ERROR('ERROR: URL de produccion detectada'))
                    
            else:
                self.stdout.write(self.style.ERROR(f'ERROR: {result.get("response", {})}'))
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'ERROR: {str(e)}'))
            
        self.stdout.write('==========================================')
