"""
Servicio de autenticación por teléfono usando Firebase Authentication
"""
import logging
from django.conf import settings
import json
import time

logger = logging.getLogger(__name__)

class FirebasePhoneAuth:
    def __init__(self):
        self.firebase_config = {
            'apiKey': getattr(settings, 'FIREBASE_API_KEY', ''),
            'authDomain': getattr(settings, 'FIREBASE_AUTH_DOMAIN', ''),
            'projectId': getattr(settings, 'FIREBASE_PROJECT_ID', ''),
            'storageBucket': getattr(settings, 'FIREBASE_STORAGE_BUCKET', ''),
            'messagingSenderId': getattr(settings, 'FIREBASE_MESSAGING_SENDER_ID', ''),
            'appId': getattr(settings, 'FIREBASE_APP_ID', ''),
        }
    
    def generate_otp_code(self):
        """
        Genera un código OTP de 6 dígitos
        """
        import random
        return ''.join(random.choices('0123456789', k=6))
    
    def create_phone_auth_data(self, phone_number, otp_code):
        """
        Crea los datos necesarios para la autenticación por teléfono
        """
        return {
            'phone_number': self._clean_phone_number(phone_number),
            'otp_code': otp_code,
            'timestamp': time.time(),
            'firebase_config': self.firebase_config
        }
    
    def _clean_phone_number(self, phone_number):
        """
        Limpia y valida el número de teléfono para Firebase
        """
        if not phone_number:
            return None
            
        # Remover caracteres no numéricos
        clean = ''.join(filter(str.isdigit, phone_number))
        
        # Firebase requiere formato internacional
        # Si empieza con 57 (Colombia), mantenerlo
        if clean.startswith('57') and len(clean) == 12:
            return f"+{clean}"
        
        # Si empieza con 3 y tiene 10 dígitos, agregar código de país
        if clean.startswith('3') and len(clean) == 10:
            return f"+57{clean}"
        
        # Si ya tiene formato internacional
        if clean.startswith('57') and len(clean) >= 10:
            return f"+{clean}"
            
        return None

# Instancia global del servicio
firebase_phone_auth = FirebasePhoneAuth()
