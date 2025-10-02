"""
Servicio para integración con ePayco
"""
try:
    from epayco.epayco import Epayco
except ImportError:
    # Fallback para desarrollo sin el SDK instalado
    Epayco = None
    
from django.conf import settings
import uuid
import requests


class EpaycoService:
    """Clase para manejar las operaciones con ePayco"""
    
    def __init__(self):
        """Inicializar cliente de ePayco"""
        if Epayco is None:
            self.client = None
        else:
            self.client = Epayco({
                "apiKey": settings.EPAYCO_PUBLIC_KEY,
                "privateKey": settings.EPAYCO_PRIVATE_KEY,
                "lenguage": "ES",
                "test": settings.EPAYCO_TEST_MODE
            })
    
    def create_payment_reference(self, order):
        """
        Crear una referencia única para el pago
        
        Args:
            order: Instancia del pedido
            
        Returns:
            str: Referencia única del pago
        """
        return f"AGC-{order.id}-{uuid.uuid4().hex[:8].upper()}"
    
    def prepare_payment_data(self, order, user, reference):
        """
        Preparar datos para el pago con ePayco
        
        Args:
            order: Instancia del pedido
            user: Usuario que realiza el pago
            reference: Referencia única del pago
            
        Returns:
            dict: Datos formateados para ePayco
        """
        return {
            "name": f"Pedido #{order.id} - {order.publicacion.cultivo.nombre_producto}",
            "description": f"Compra de {order.cantidad_acordada} {order.publicacion.unidad_medida} de {order.publicacion.cultivo.nombre_producto}",
            "invoice": reference,
            "currency": "COP",
            "amount": str(order.precio_total),
            "tax_base": "0",
            "tax": "0",
            "country": "CO",
            "lang": "es",
            
            # Información del comprador
            "external": "false",
            "extra1": f"order_{order.id}",
            "extra2": user.email,
            "extra3": user.get_full_name() or user.username,
            
            # URLs de respuesta
            "response": settings.EPAYCO_RESPONSE_URL,
            "confirmation": settings.EPAYCO_CONFIRMATION_URL,
            
            # Información del cliente
            "name_billing": user.get_full_name() or user.username,
            "type_doc_billing": "CC",
            "mobilephone_billing": getattr(user, 'telefono', ''),
            "number_doc_billing": getattr(user, 'cedula', ''),
        }
    
    def create_checkout_session(self, order, user):
        """
        Crear una sesión de checkout con ePayco
        
        Args:
            order: Instancia del pedido
            user: Usuario que realiza el pago
            
        Returns:
            dict: Datos de la sesión de checkout
        """
        reference = self.create_payment_reference(order)
        payment_data = self.prepare_payment_data(order, user, reference)
        
        return {
            'reference': reference,
            'payment_data': payment_data,
            'public_key': settings.EPAYCO_PUBLIC_KEY,
            'test_mode': settings.EPAYCO_TEST_MODE
        }
    
    def verify_transaction(self, transaction_id):
        """
        Verificar el estado de una transacción con ePayco
        
        Args:
            transaction_id: ID de la transacción en ePayco
            
        Returns:
            dict: Datos de la transacción
        """
        try:
            response = self.client.charge.get(transaction_id)
            return response
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def process_confirmation(self, data):
        """
        Procesar confirmación de pago desde ePayco
        
        Args:
            data: Datos recibidos de ePayco
            
        Returns:
            dict: Resultado del procesamiento
        """
        try:
            # Extraer información relevante
            x_ref_payco = data.get('x_ref_payco')
            x_transaction_id = data.get('x_transaction_id')
            x_amount = data.get('x_amount')
            x_currency_code = data.get('x_currency_code')
            x_signature = data.get('x_signature')
            x_approval_code = data.get('x_approval_code')
            x_response = data.get('x_response')
            x_response_reason_text = data.get('x_response_reason_text')
            x_transaction_state = data.get('x_transaction_state')
            
            # Verificar firma (opcional pero recomendado)
            # TODO: Implementar verificación de firma
            
            return {
                'success': True,
                'ref_payco': x_ref_payco,
                'transaction_id': x_transaction_id,
                'amount': x_amount,
                'currency': x_currency_code,
                'approved': x_response == 'Aceptada',
                'state': x_transaction_state,
                'response_text': x_response_reason_text,
                'approval_code': x_approval_code,
                'raw_data': data
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_data': data
            }

