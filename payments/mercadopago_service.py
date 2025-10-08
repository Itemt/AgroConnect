"""
Servicio para integración con MercadoPago
"""
import mercadopago
from django.conf import settings
import uuid
from decouple import config


class MercadoPagoService:
    """Clase para manejar las operaciones con MercadoPago"""
    
    def __init__(self):
        """Inicializar cliente de MercadoPago"""
        self.access_token = config('MERCADOPAGO_ACCESS_TOKEN', default='')
        
        # Fallback temporal para desarrollo
        if not self.access_token:
            # Token de producción actualizado
            self.access_token = 'APP_USR-556738036241163-100800-274b8aac5e1bff0d9609efceaaaf736b-2911063518'
            print("INFO: Usando credenciales de producción actualizadas")
            print("INFO: Modo producción activado")
        
        if self.access_token:
            self.sdk = mercadopago.SDK(self.access_token)
        else:
            self.sdk = None
    
    def create_payment_reference(self, order):
        """
        Crear una referencia única para el pago
        
        Args:
            order: Instancia del pedido
            
        Returns:
            str: Referencia única del pago
        """
        return f"AGC-{order.id}-{uuid.uuid4().hex[:8].upper()}"
    
    def _ensure_json_serializable(self, data):
        """
        Convertir todos los valores Decimal a float para serialización JSON
        
        Args:
            data: Diccionario con datos del pago
            
        Returns:
            dict: Diccionario con valores convertidos
        """
        from decimal import Decimal
        
        def convert_value(value):
            if isinstance(value, Decimal):
                return float(value)
            elif isinstance(value, dict):
                return {k: convert_value(v) for k, v in value.items()}
            elif isinstance(value, list):
                return [convert_value(item) for item in value]
            else:
                return value
        
        return convert_value(data)
    
    def prepare_payment_data(self, order, user, reference):
        """
        Preparar datos para el pago con MercadoPago
        
        Args:
            order: Instancia del pedido
            user: Usuario que realiza el pago
            reference: Referencia única del pago
            
        Returns:
            dict: Datos formateados para MercadoPago
        """
        # Obtener información del usuario de forma segura
        full_name = user.get_full_name() or user.username or "Usuario"
        email = user.email or ""
        
        return {
            "transaction_amount": float(order.precio_total),
            "currency_id": "COP",
            "description": f"Compra de {order.cantidad_acordada} {order.publicacion.cultivo.unidad_medida} de {order.publicacion.cultivo.nombre}",
            "payment_method_id": "pse",  # PSE por defecto para Colombia
            "payer": {
                "email": email,
                "identification": {
                    "type": "CC",
                    "number": getattr(user, 'cedula', '') or "12345678"
                },
                "name": full_name
            },
            "external_reference": reference,
            "notification_url": f"{settings.ALLOWED_HOSTS[0] if settings.ALLOWED_HOSTS else 'localhost:8000'}/payments/notification/",
            "additional_info": {
                "items": [
                    {
                        "id": str(order.publicacion.id),
                        "title": order.publicacion.cultivo.nombre,
                        "description": f"{order.cantidad_acordada} {order.publicacion.cultivo.unidad_medida}",
                        "quantity": float(order.cantidad_acordada),
                        "unit_price": float(order.publicacion.precio_por_unidad),
                        "category_id": "food",
                        "currency_id": "COP"
                    }
                ],
                "payer": {
                    "first_name": user.first_name or "",
                    "last_name": user.last_name or "",
                    "phone": {
                        "area_code": "57",
                        "number": getattr(user, 'telefono', '') or "3000000000"
                    },
                    "address": {
                        "zip_code": "110111",
                        "street_name": "Calle",
                        "street_number": 123
                    }
                }
            }
        }
    
    def create_preference(self, order, user):
        """
        Crear una preferencia de pago con MercadoPago
        
        Args:
            order: Instancia del pedido
            user: Usuario que realiza el pago
            
        Returns:
            dict: Datos de la preferencia de pago
        """
        if not self.sdk:
            return {
                'success': False,
                'error': 'MercadoPago no configurado. Verifica que MERCADOPAGO_ACCESS_TOKEN esté configurado en las variables de entorno.'
            }
        
        try:
            reference = self.create_payment_reference(order)
            
            # Obtener la URL base dinámicamente
            try:
                from django.contrib.sites.models import Site
                current_site = Site.objects.get_current()
                base_url = f"https://{current_site.domain}" if not settings.DEBUG else "https://agroconnect.itemt.tech"
            except:
                # Fallback si Site no está disponible
                base_url = "https://agroconnect.itemt.tech"
            
            # Configuración específica para modo sandbox
            is_sandbox = self.access_token.startswith('TEST-')
            
            # Para sandbox en producción, usar URLs más simples
            if is_sandbox and not settings.DEBUG:
                base_url = "https://agroconnect.itemt.tech"
            
            # Datos para MercadoPago - configuración corregida para sandbox
            # Usar email de prueba específico para sandbox
            test_email = "test_user_123456@testuser.com" if is_sandbox else (user.email or "test@example.com")
            
            # Para proyecto universitario: usar datos específicos de sandbox
            if is_sandbox:
                # Usar las cuentas específicas de MercadoPago Sandbox
                test_email = "TESTUSER8283595198251736383@testuser.com"  # Comprador
                payer_name = "Test User"
                payer_surname = "University"
            else:
                # Para credenciales de producción de cuenta de prueba
                # Usar datos completos para evitar botón gris
                test_email = user.email or "test@example.com"
                payer_name = user.get_full_name() or user.username or "Usuario"
                payer_surname = user.last_name or "Prueba"
                
                # Asegurar que el email sea válido
                if not test_email or "@" not in test_email:
                    test_email = "test@agroconnect.com"
            
            # Forzar modo sandbox para proyecto universitario
            if is_sandbox:
                # Configuración específica para forzar sandbox
                payment_data = {
                    "transaction_amount": float(order.precio_total),
                    "currency_id": "COP",
                    "description": f"Compra orden #{order.id} - Proyecto Universitario",
                    "payer": {
                        "email": test_email,
                        "name": payer_name,
                        "surname": payer_surname
                    },
                    "external_reference": reference,
                    "notification_url": f"{base_url}/payments/notification/",
                    "auto_return": "approved",
                    "back_urls": {
                        "success": f"{base_url}/payments/success/",
                        "failure": f"{base_url}/payments/failure/",
                        "pending": f"{base_url}/payments/pending/"
                    },
                # Configuración específica para sandbox
                "statement_descriptor": "AGROCONNECT",
                "binary_mode": False,
                "expires": False,
                # Configuración para evitar botón gris
                "differential_pricing_id": None,
                "marketplace": "NONE",
                "processing_mode": "aggregator",
                    "metadata": {
                        "test": True,
                        "platform": "agroconnect",
                        "version": "1.0",
                        "university_project": True
                    },
                    # Configuración de métodos de pago para sandbox
                    "payment_methods": {
                        "excluded_payment_methods": [],
                        "excluded_payment_types": [],
                        "installments": 1,
                        "default_installments": 1
                    },
                    "items": [
                        {
                            "id": str(order.publicacion.id),
                            "title": order.publicacion.cultivo.nombre,
                            "description": f"{order.cantidad_acordada} {order.publicacion.cultivo.unidad_medida}",
                            "quantity": float(order.cantidad_acordada),
                            "unit_price": float(order.publicacion.precio_por_unidad),
                            "category_id": "food",
                            "currency_id": "COP"
                        }
                    ]
                }
            else:
                # Configuración normal para producción
                payment_data = {
                    "transaction_amount": float(order.precio_total),
                    "currency_id": "COP",
                    "description": f"Compra orden #{order.id}",
                    "payer": {
                        "email": test_email,
                        "name": payer_name,
                        "surname": payer_surname
                    },
                    "external_reference": reference,
                    "notification_url": f"{base_url}/payments/notification/",
                    "auto_return": "approved",
                    "back_urls": {
                        "success": f"{base_url}/payments/success/",
                        "failure": f"{base_url}/payments/failure/",
                        "pending": f"{base_url}/payments/pending/"
                    },
                    "items": [
                        {
                            "id": str(order.publicacion.id),
                            "title": order.publicacion.cultivo.nombre,
                            "description": f"{order.cantidad_acordada} {order.publicacion.cultivo.unidad_medida}",
                            "quantity": float(order.cantidad_acordada),
                            "unit_price": float(order.publicacion.precio_por_unidad),
                            "category_id": "food",
                            "currency_id": "COP"
                        }
                    ]
                }
            
            payment_data = {
                "transaction_amount": float(order.precio_total),
                "currency_id": "COP",
                "description": f"Compra orden #{order.id}",
                "payer": {
                    "email": test_email,
                    "name": payer_name,
                    "surname": payer_surname,
                    "identification": {
                        "type": "CC",
                        "number": "12345678"
                    },
                    "phone": {
                        "area_code": "57",
                        "number": "3000000000"
                    },
                    "address": {
                        "zip_code": "110111",
                        "street_name": "Calle 123",
                        "street_number": 123,
                        "neighborhood": "Centro",
                        "city": "Bogotá",
                        "federal_unit": "Cundinamarca"
                    }
                },
                "external_reference": reference,
                "notification_url": f"{base_url}/payments/notification/",
                "auto_return": "approved",
                "back_urls": {
                    "success": f"{base_url}/payments/success/",
                    "failure": f"{base_url}/payments/failure/",
                    "pending": f"{base_url}/payments/pending/"
                },
                # Configuración específica para sandbox en producción
                "statement_descriptor": "AGROCONNECT",
                # Configuración optimizada para sandbox
                "binary_mode": False,
                "expires": False,
                # Configuración específica para sandbox
                "metadata": {
                    "test": is_sandbox,
                    "platform": "agroconnect",
                    "version": "1.0"
                },
                # Configuración de métodos de pago para sandbox
                "payment_methods": {
                    "excluded_payment_methods": [],
                    "excluded_payment_types": [],
                    "installments": 1,
                    "default_installments": 1
                },
                # Configuración específica para tarjetas en sandbox
                "card_token": None,
                "capture": True,
                "items": [
                    {
                        "id": str(order.publicacion.id),
                        "title": order.publicacion.cultivo.nombre[:50],
                        "description": f"{order.cantidad_acordada} {order.publicacion.cultivo.unidad_medida}"[:100],
                        "quantity": float(order.cantidad_acordada),
                        "unit_price": float(order.publicacion.precio_por_unidad),
                        "category_id": "food",
                        "currency_id": "COP"
                    }
                ]
            }
            
            # Configuración adicional para sandbox
            if is_sandbox:
                payment_data["test_mode"] = True
                # Agregar información específica del comprador para sandbox
                payment_data["payer"]["identification"] = {
                    "type": "CC",
                    "number": "12345678"
                }
                
                # Configuración específica para sandbox en producción
                if not settings.DEBUG:
                    # En producción con sandbox, usar configuración más permisiva para tarjetas
                    payment_data["payment_methods"] = {
                        "excluded_payment_methods": [],
                        "excluded_payment_types": [],
                        "installments": 1,
                        "default_installments": 1,
                        # Configuración específica para mejorar compatibilidad con tarjetas
                        "default_payment_method_id": None,
                        "excluded_payment_methods": [],
                        "excluded_payment_types": []
                    }
                    # Agregar configuración de mercado específica para Colombia
                    payment_data["marketplace"] = "NONE"
                    payment_data["differential_pricing_id"] = None
                    
                    # Configuración adicional para mejorar compatibilidad con tarjetas
                    payment_data["processing_mode"] = "aggregator"
                    payment_data["merchant_account_id"] = None
                
                print("🧪 Configuración de sandbox aplicada")
                if not settings.DEBUG:
                    print("⚠️ Sandbox en producción - usando configuración especial")
                print("📋 Para evitar el error 'Algo salió mal':")
                print("   1. Usa un usuario de prueba de MercadoPago")
                print("   2. Email de prueba: test_user_123456@testuser.com")
                print("   3. Tarjetas de prueba que funcionan:")
                print("      - Visa: 4509 9535 6623 3704")
                print("      - Mastercard: 5031 7557 3453 0604")
                print("      - CVV: 123, Vencimiento: 11/25, Nombre: APRO")
                print("   4. Si no funciona, prueba con PSE o Efecty")
                print("   5. En producción con sandbox, PSE y Efecty son más estables")
            
            # Validar datos antes de enviar
            if payment_data['transaction_amount'] <= 0:
                return {
                    'success': False,
                    'error': 'El monto de la transacción debe ser mayor a 0'
                }
            
            if not payment_data['payer']['email']:
                return {
                    'success': False,
                    'error': 'El email del pagador es requerido'
                }
            
            print(f"=== DEBUG PREFERENCE DATA ===")
            print(f"Transaction amount: {payment_data['transaction_amount']}")
            print(f"Currency: {payment_data['currency_id']}")
            print(f"Description: {payment_data['description']}")
            print(f"External reference: {payment_data['external_reference']}")
            print(f"Base URL: {base_url}")
            print("=============================")
            
            # Crear preferencia
            preference_response = self.sdk.preference().create(payment_data)
            
            print(f"=== DEBUG PREFERENCE RESPONSE ===")
            print(f"Status: {preference_response.get('status')}")
            print(f"Response keys: {list(preference_response.keys())}")
            if 'response' in preference_response:
                print(f"Response ID: {preference_response['response'].get('id')}")
                print(f"Init Point: {preference_response['response'].get('init_point')}")
            if 'error' in preference_response:
                print(f"Error: {preference_response['error']}")
            print("================================")
            
            if preference_response.get("status") == 201 and "response" in preference_response:
                response_data = preference_response["response"]
                if "id" in response_data and "init_point" in response_data:
                    return {
                        'success': True,
                        'preference_id': response_data["id"],
                        'init_point': response_data["init_point"],
                        'reference': reference
                    }
                else:
                    return {
                        'success': False,
                        'error': "Respuesta de MercadoPago incompleta - faltan campos requeridos",
                        'response': preference_response
                    }
            else:
                error_message = "Error desconocido"
                if "error" in preference_response:
                    error_message = preference_response["error"]
                elif "message" in preference_response:
                    error_message = preference_response["message"]
                
                return {
                    'success': False,
                    'error': f"Error al crear preferencia. Status: {preference_response.get('status')}. {error_message}",
                    'response': preference_response
                }
                
        except Exception as e:
            print(f"=== DEBUG EXCEPTION ===")
            print(f"Exception type: {type(e)}")
            print(f"Exception message: {str(e)}")
            print("======================")
            return {
                'success': False,
                'error': str(e)
            }
    
    def simulate_automatic_payment(self, order, user):
        """
        Simular pago automático para proyecto universitario
        """
        import uuid
        from django.utils import timezone
        
        # Crear datos simulados de pago
        simulated_payment_data = {
            'success': True,
            'payment_id': f"MP-{uuid.uuid4().hex[:8].upper()}",
            'status': 'approved',
            'status_detail': 'accredited',
            'transaction_amount': float(order.precio_total),
            'currency_id': 'COP',
            'external_reference': self.create_payment_reference(order),
            'payment_method_id': 'pse',
            'date_approved': timezone.now().isoformat(),
            'date_created': timezone.now().isoformat(),
            'raw_data': {
                'id': f"MP-{uuid.uuid4().hex[:8].upper()}",
                'status': 'approved',
                'status_detail': 'accredited',
                'transaction_amount': float(order.precio_total),
                'currency_id': 'COP',
                'external_reference': self.create_payment_reference(order),
                'payment_method_id': 'pse',
                'date_approved': timezone.now().isoformat(),
                'date_created': timezone.now().isoformat()
            }
        }
        
        return simulated_payment_data
    
    def get_payment_info(self, payment_id):
        """
        Obtener información de un pago específico
        
        Args:
            payment_id: ID del pago en MercadoPago
            
        Returns:
            dict: Información del pago
        """
        if not self.sdk:
            return {
                'success': False,
                'error': 'MercadoPago no configurado. Verifica que MERCADOPAGO_ACCESS_TOKEN esté configurado en las variables de entorno.'
            }
        
        try:
            payment_response = self.sdk.payment().get(payment_id)
            
            if payment_response["status"] == 200:
                payment = payment_response["response"]
                return {
                    'success': True,
                    'payment_id': payment["id"],
                    'status': payment["status"],
                    'status_detail': payment["status_detail"],
                    'transaction_amount': payment["transaction_amount"],
                    'currency_id': payment["currency_id"],
                    'external_reference': payment["external_reference"],
                    'payment_method_id': payment["payment_method_id"],
                    'date_approved': payment.get("date_approved"),
                    'date_created': payment.get("date_created"),
                    'raw_data': payment
                }
            else:
                return {
                    'success': False,
                    'error': 'Error al obtener información del pago',
                    'response': payment_response
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_webhook(self, data):
        """
        Procesar webhook de MercadoPago
        
        Args:
            data: Datos recibidos del webhook
            
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            # MercadoPago envía el ID del pago en el webhook
            payment_id = data.get('data', {}).get('id')
            
            if not payment_id:
                return {
                    'success': False,
                    'error': 'ID de pago no encontrado en webhook'
                }
            
            # Obtener información del pago
            payment_info = self.get_payment_info(payment_id)
            
            if payment_info['success']:
                return {
                    'success': True,
                    'payment_id': payment_info['payment_id'],
                    'status': payment_info['status'],
                    'status_detail': payment_info['status_detail'],
                    'transaction_amount': payment_info['transaction_amount'],
                    'external_reference': payment_info['external_reference'],
                    'approved': payment_info['status'] == 'approved',
                    'raw_data': payment_info['raw_data']
                }
            else:
                return payment_info
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_data': data
            }
