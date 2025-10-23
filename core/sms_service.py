"""
Servicio de envío de SMS usando Firebase Authentication
"""
import logging
from django.conf import settings
import firebase_admin
from firebase_admin import auth, credentials
import os

logger = logging.getLogger(__name__)

class FirebaseSMSService:
    def __init__(self):
        self.initialized = False
        self._initialize_firebase()
        
    def _initialize_firebase(self):
        """
        Inicializa Firebase Admin SDK
        """
        try:
            if not firebase_admin._apps:
                # Obtener path del archivo de credenciales
                cred_path = getattr(settings, 'FIREBASE_ADMIN_CREDENTIALS_PATH', None)
                
                if cred_path and os.path.exists(cred_path):
                    cred = credentials.Certificate(cred_path)
                    firebase_admin.initialize_app(cred)
                    self.initialized = True
                    logger.info("Firebase Admin SDK initialized successfully")
                else:
                    logger.warning("Firebase Admin credentials not found. SMS will be simulated.")
            else:
                self.initialized = True
                
        except Exception as e:
            logger.error(f"Error initializing Firebase Admin SDK: {str(e)}")
            self.initialized = False
    
    def send_otp_sms(self, phone_number, otp_code):
        """
        Envía código OTP por SMS usando Firebase Authentication
        """
        try:
            # Limpiar número de teléfono
            clean_phone = self._clean_phone_number(phone_number)
            
            if not clean_phone:
                logger.error(f"Invalid phone number: {phone_number}")
                return False, "Número de teléfono inválido"
            
            # Para desarrollo o si Firebase no está configurado, simular envío
            if not self.initialized:
                logger.info(f"Firebase SMS OTP {otp_code} sent to {clean_phone} (simulated)")
                return True, "SMS enviado correctamente (simulado - Firebase no configurado)"
            
            # Firebase Authentication no tiene API directa para enviar SMS personalizados
            # Solo puede enviar códigos de verificación para autenticación
            # Para este caso, simularemos el envío pero con la estructura de Firebase
            
            logger.info(f"Firebase SMS OTP {otp_code} sent to {clean_phone} (simulated)")
            return True, "SMS enviado correctamente (Firebase simulado)"
            
        except Exception as e:
            logger.error(f"Error sending SMS to {phone_number}: {str(e)}")
            return False, str(e)
    
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
sms_service = FirebaseSMSService()
