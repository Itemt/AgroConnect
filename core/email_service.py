"""
Servicio de envío de correos electrónicos usando Resend
"""
import resend
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)

class EmailService:
    def __init__(self):
        self.api_key = settings.RESEND_API_KEY
        self.from_email = settings.RESEND_FROM_EMAIL
        
        if self.api_key and self.api_key.strip():
            resend.api_key = self.api_key
        else:
            logger.warning("RESEND_API_KEY not configured. Email functionality will be disabled.")
    
    def send_password_reset_email(self, user_email, reset_url, user_name=None, recovery_code=None):
        """
        Envía correo de recuperación de contraseña
        """
        # Verificar si la API key está configurada
        if not self.api_key or not self.api_key.strip():
            error_msg = "API key is invalid"
            logger.error(f"Email service not configured: {error_msg}")
            return False, error_msg
            
        try:
            context = {
                'user_name': user_name or 'Usuario',
                'reset_url': reset_url,
                'recovery_code': recovery_code,
                'site_name': 'AgroConnect'
            }
            
            # Renderizar template HTML del email
            html_content = render_to_string('accounts/password_reset_email_template.html', context)
            text_content = strip_tags(html_content)
            
            params = {
                "from": self.from_email,
                "to": [user_email],
                "subject": "Recupera tu contraseña - AgroConnect",
                "html": html_content,
                "text": text_content,
            }
            
            email = resend.Emails.send(params)
            logger.info(f"Password reset email sent successfully to {user_email}")
            return True, email
            
        except Exception as e:
            logger.error(f"Error sending password reset email to {user_email}: {str(e)}")
            return False, str(e)
    
    def send_otp_sms_notification(self, phone_number, otp_code):
        """
        Notifica que se envió OTP por SMS (para logging)
        """
        logger.info(f"OTP {otp_code} sent to phone {phone_number}")
        return True
    
    def send_order_confirmation_email(self, user_email, order, user_name=None):
        """
        Envía confirmación de pedido (usa el nuevo template con QR)
        """
        # Este método ahora usa send_order_buyer_confirmation_email con los nuevos templates
        from sales.qr_utils import get_order_buyer_qr
        
        try:
            buyer_qr = get_order_buyer_qr(order)
            buyer_url = order.get_buyer_qr_url()
            
            context = {
                'user_name': user_name or 'Usuario',
                'order': order,
                'qr_code': buyer_qr,
                'order_url': buyer_url,
                'site_name': 'AgroConnect'
            }
            
            html_content = render_to_string('sales/order_buyer_confirmation_email.html', context)
            text_content = strip_tags(html_content)
            
            params = {
                "from": self.from_email,
                "to": [user_email],
                "subject": f"Confirmación de pedido #{order.id} - AgroConnect",
                "html": html_content,
                "text": text_content,
            }
            
            email = resend.Emails.send(params)
            logger.info(f"Order confirmation email sent successfully to {user_email}")
            return True, email
            
        except Exception as e:
            logger.error(f"Error sending order confirmation email to {user_email}: {str(e)}")
            return False, str(e)

    def send_order_paid_seller_email(self, seller_email, order, seller_name=None):
        """
        Notifica al vendedor que recibió un pedido con pago aprobado
        """
        try:
            context = {
                'seller_name': seller_name or 'Productor',
                'order': order,
                'site_name': 'AgroConnect'
            }
            html_content = render_to_string('sales/order_paid_seller_email.html', context)
            text_content = strip_tags(html_content)
            params = {
                "from": self.from_email,
                "to": [seller_email],
                "subject": f"Pago aprobado del pedido #{order.id} - AgroConnect",
                "html": html_content,
                "text": text_content,
            }
            email = resend.Emails.send(params)
            logger.info(f"Seller order paid email sent successfully to {seller_email}")
            return True, email
        except Exception as e:
            logger.error(f"Error sending seller order paid email to {seller_email}: {str(e)}")
            return False, str(e)
    
    def send_order_buyer_confirmation_email(self, buyer_email, order, buyer_name=None, qr_code=None, order_url=None):
        """
        Envía confirmación de compra al comprador con código QR
        """
        if not self.api_key or not self.api_key.strip():
            error_msg = "API key is invalid"
            logger.error(f"Email service not configured: {error_msg}")
            return False, error_msg
            
        try:
            context = {
                'user_name': buyer_name or 'Usuario',
                'order': order,
                'qr_code': qr_code,
                'order_url': order_url,
                'site_name': 'AgroConnect'
            }
            
            html_content = render_to_string('sales/order_buyer_confirmation_email.html', context)
            text_content = strip_tags(html_content)
            
            params = {
                "from": self.from_email,
                "to": [buyer_email],
                "subject": f"Confirmación de compra - Pedido #{order.id} - AgroConnect",
                "html": html_content,
                "text": text_content,
            }
            
            email = resend.Emails.send(params)
            logger.info(f"Buyer confirmation email sent successfully to {buyer_email}")
            return True, email
            
        except Exception as e:
            logger.error(f"Error sending buyer confirmation email to {buyer_email}: {str(e)}")
            return False, str(e)
    
    def send_order_seller_notification_email(self, seller_email, order, seller_name=None, qr_code=None, order_url=None):
        """
        Notifica al vendedor sobre una nueva venta con código QR
        """
        if not self.api_key or not self.api_key.strip():
            error_msg = "API key is invalid"
            logger.error(f"Email service not configured: {error_msg}")
            return False, error_msg
            
        try:
            context = {
                'seller_name': seller_name or 'Vendedor',
                'order': order,
                'qr_code': qr_code,
                'order_url': order_url,
                'site_name': 'AgroConnect'
            }
            
            html_content = render_to_string('sales/order_seller_notification_email.html', context)
            text_content = strip_tags(html_content)
            
            params = {
                "from": self.from_email,
                "to": [seller_email],
                "subject": f"Nueva venta recibida - Pedido #{order.id} - AgroConnect",
                "html": html_content,
                "text": text_content,
            }
            
            email = resend.Emails.send(params)
            logger.info(f"Seller notification email sent successfully to {seller_email}")
            return True, email
            
        except Exception as e:
            logger.error(f"Error sending seller notification email to {seller_email}: {str(e)}")
            return False, str(e)
    
    def send_order_in_transit_email(self, buyer_email, order, buyer_name=None, qr_code=None, order_url=None):
        """
        Notifica al comprador que su pedido está en tránsito con código QR
        """
        if not self.api_key or not self.api_key.strip():
            error_msg = "API key is invalid"
            logger.error(f"Email service not configured: {error_msg}")
            return False, error_msg
            
        try:
            context = {
                'user_name': buyer_name or 'Usuario',
                'order': order,
                'qr_code': qr_code,
                'order_url': order_url,
                'site_name': 'AgroConnect'
            }
            
            html_content = render_to_string('sales/order_in_transit_email.html', context)
            text_content = strip_tags(html_content)
            
            params = {
                "from": self.from_email,
                "to": [buyer_email],
                "subject": f"Tu pedido está en camino - Pedido #{order.id} - AgroConnect",
                "html": html_content,
                "text": text_content,
            }
            
            email = resend.Emails.send(params)
            logger.info(f"In transit email sent successfully to {buyer_email}")
            return True, email
            
        except Exception as e:
            logger.error(f"Error sending in transit email to {buyer_email}: {str(e)}")
            return False, str(e)
    
    def send_order_received_seller_email(self, seller_email, order, seller_name=None, qr_code=None, order_url=None, buyer_rating=None, seller_rating=None):
        """
        Notifica al vendedor que el comprador recibió el producto con código QR
        """
        if not self.api_key or not self.api_key.strip():
            error_msg = "API key is invalid"
            logger.error(f"Email service not configured: {error_msg}")
            return False, error_msg
            
        try:
            context = {
                'seller_name': seller_name or 'Vendedor',
                'order': order,
                'qr_code': qr_code,
                'order_url': order_url,
                'buyer_rating': buyer_rating,
                'seller_rating': seller_rating,
                'site_name': 'AgroConnect'
            }
            
            html_content = render_to_string('sales/order_received_seller_email.html', context)
            text_content = strip_tags(html_content)
            
            params = {
                "from": self.from_email,
                "to": [seller_email],
                "subject": f"¡Venta completada! - Pedido #{order.id} - AgroConnect",
                "html": html_content,
                "text": text_content,
            }
            
            email = resend.Emails.send(params)
            logger.info(f"Order received seller email sent successfully to {seller_email}")
            return True, email
            
        except Exception as e:
            logger.error(f"Error sending order received seller email to {seller_email}: {str(e)}")
            return False, str(e)

# Instancia global del servicio
email_service = EmailService()
