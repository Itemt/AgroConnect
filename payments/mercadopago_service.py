"""
Servicio para integración con MercadoPago
"""
import mercadopago
from django.conf import settings
import uuid
from decouple import config
import logging

logger = logging.getLogger(__name__)


class MercadoPagoService:
    """Clase para manejar las operaciones con MercadoPago"""
    
    def __init__(self):
        """Inicializar cliente de MercadoPago"""
        self.access_token = config('MERCADOPAGO_ACCESS_TOKEN', default='')
        
        # Fallback temporal para desarrollo
        if not self.access_token:
            # Token de producción actualizado
            self.access_token = 'YOUR_MERCADOPAGO_ACCESS_TOKEN_HERE'
            logger.info("Usando credenciales de producción actualizadas")
            logger.info("Modo producción activado")
        
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
            "notification_url": "https://agroconnect.itemt.tech/payments/notification/",
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
            
            # Obtener la URL base - SIEMPRE usar la URL de producción
            # No usar Site.objects.get_current() porque puede tener example.com
            base_url = "https://agroconnect.itemt.tech"
            
            # Configuración específica para modo sandbox
            is_sandbox = self.access_token.startswith('TEST-')
            
            # Preparar datos del pagador - CRÍTICO para evitar botón gris
            # Asegurar que el email sea válido y esté presente
            payer_email = user.email or "test@agroconnect.com"
            if not payer_email or "@" not in payer_email:
                payer_email = "test@agroconnect.com"
            
            # Para modo sandbox, usar email de prueba específico
            if is_sandbox:
                payer_email = "TESTUSER8283595198251736383@testuser.com"
            
            # Preparar nombre y apellido del pagador
            full_name = user.get_full_name() or user.username or "Usuario"
            name_parts = full_name.split(' ', 1) if ' ' in full_name else [full_name, '']
            payer_name = name_parts[0] or "Usuario"
            payer_surname = name_parts[1] if len(name_parts) > 1 else (user.last_name or "Prueba")
            
            # Obtener identificación del usuario
            user_cedula = getattr(user, 'cedula', '') or "12345678"
            user_phone = getattr(user, 'telefono', '') or "3000000000"
            
            # Limpiar teléfono (solo números)
            user_phone = ''.join(filter(str.isdigit, str(user_phone)))
            if len(user_phone) < 10:
                user_phone = "3000000000"
            
            # Preparar datos de la preferencia - estructura única y completa
            payment_data = {
                "transaction_amount": float(order.precio_total),
                "currency_id": "COP",
                "description": f"Compra orden #{order.id}",
                "payer": {
                    "email": payer_email,
                    "name": payer_name,
                    "surname": payer_surname,
                    "identification": {
                        "type": "CC",
                        "number": str(user_cedula)[:20]  # Limitar longitud
                    },
                    "phone": {
                        "area_code": "57",
                        "number": user_phone[-10:]  # Últimos 10 dígitos
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
                "statement_descriptor": "AGROCONNECT",
                "binary_mode": False,
                "expires": False,
                "metadata": {
                    "test": is_sandbox,
                    "platform": "agroconnect",
                    "version": "1.0",
                    "order_id": str(order.id)
                },
                "payment_methods": {
                    "excluded_payment_methods": [],
                    "excluded_payment_types": [],
                    "installments": 1,
                    "default_installments": 1
                },
                "items": [
                    {
                        "id": str(order.publicacion.id),
                        "title": str(order.publicacion.cultivo.nombre)[:50],  # Limitar longitud
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
                payment_data["payer"]["name"] = "Test User"
                payment_data["payer"]["surname"] = "University"
                payment_data["payer"]["identification"]["number"] = "12345678"
            
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
            
            logger.info("Preference data prepared")
            logger.info(f"Transaction amount: {payment_data['transaction_amount']}")
            logger.info(f"Currency: {payment_data['currency_id']}")
            logger.info(f"Description: {payment_data['description']}")
            logger.info(f"External reference: {payment_data['external_reference']}")
            logger.info(f"Base URL: {base_url}")
            
            # Crear preferencia
            preference_response = self.sdk.preference().create(payment_data)
            
            logger.info("Preference response received")
            logger.info(f"Status: {preference_response.get('status')}")
            logger.info(f"Response keys: {list(preference_response.keys())}")
            if 'response' in preference_response:
                logger.info(f"Response ID: {preference_response['response'].get('id')}")
                logger.info(f"Init Point: {preference_response['response'].get('init_point')}")
            if 'error' in preference_response:
                logger.error(f"Error: {preference_response['error']}")
            
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
            logger.error(f"Exception in MercadoPago service: {str(e)}")
            logger.error(f"Exception type: {type(e)}")
            logger.error(f"Exception message: {str(e)}")
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
