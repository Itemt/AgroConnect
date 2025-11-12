"""
Utilidades para generar códigos QR para pedidos
"""
import qrcode
from io import BytesIO
import base64
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


def generate_qr_code(data, size=10, border=1):
    """
    Genera un código QR a partir de datos
    
    Args:
        data: String o URL para codificar en el QR
        size: Tamaño del código QR (default 10)
        border: Grosor del borde (default 1)
        
    Returns:
        String con la imagen en formato base64 para usar en img src
    """
    try:
        # Crear el código QR
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=size,
            border=border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        # Generar la imagen
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convertir a base64
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return f"data:image/png;base64,{img_str}"
    
    except Exception as e:
        logger.error(f"Error generando código QR: {e}")
        return None


def get_order_buyer_qr(order):
    """
    Obtiene el código QR para el comprador de un pedido
    
    Args:
        order: Instancia del modelo Order
        
    Returns:
        String con la imagen en formato base64
    """
    # Intentar obtener del cache primero
    cache_key = f"order_qr_buyer_{order.id}"
    cached_qr = cache.get(cache_key)
    
    if cached_qr:
        return cached_qr
    
    # Generar el QR
    url = order.get_buyer_qr_url()
    qr_code = generate_qr_code(url, size=8, border=2)
    
    # Guardar en cache por 7 días (los tokens no cambian)
    if qr_code:
        cache.set(cache_key, qr_code, 60 * 60 * 24 * 7)
    
    return qr_code


def get_order_seller_qr(order):
    """
    Obtiene el código QR para el vendedor de un pedido
    
    Args:
        order: Instancia del modelo Order
        
    Returns:
        String con la imagen en formato base64
    """
    # Intentar obtener del cache primero
    cache_key = f"order_qr_seller_{order.id}"
    cached_qr = cache.get(cache_key)
    
    if cached_qr:
        return cached_qr
    
    # Generar el QR
    url = order.get_seller_qr_url()
    qr_code = generate_qr_code(url, size=8, border=2)
    
    # Guardar en cache por 7 días (los tokens no cambian)
    if qr_code:
        cache.set(cache_key, qr_code, 60 * 60 * 24 * 7)
    
    return qr_code

