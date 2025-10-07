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
                'error': 'MercadoPago no configurado'
            }
        
        try:
            reference = self.create_payment_reference(order)
            payment_data = self.prepare_payment_data(order, user, reference)
            
            # Asegurar que todos los valores numéricos sean float
            payment_data = self._ensure_json_serializable(payment_data)
            
            # Crear preferencia
            preference_response = self.sdk.preference().create(payment_data)
            
            if preference_response["status"] == 201:
                return {
                    'success': True,
                    'preference_id': preference_response["response"]["id"],
                    'init_point': preference_response["response"]["init_point"],
                    'reference': reference
                }
            else:
                return {
                    'success': False,
                    'error': 'Error al crear preferencia',
                    'response': preference_response
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
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
                'error': 'MercadoPago no configurado'
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
