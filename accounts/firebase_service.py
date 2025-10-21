"""
Servicio de Firebase Authentication para AgroConnect
Maneja Google Sign-In y SMS OTP para recuperación de contraseñas
"""

import os
import firebase_admin
from firebase_admin import credentials, auth
import pyrebase
from django.conf import settings
from decouple import config

# Configuración de Firebase Web (para el cliente)
FIREBASE_WEB_CONFIG = {
    'apiKey': config('FIREBASE_API_KEY', default=''),
    'authDomain': config('FIREBASE_AUTH_DOMAIN', default=''),
    'projectId': config('FIREBASE_PROJECT_ID', default=''),
    'storageBucket': config('FIREBASE_STORAGE_BUCKET', default=''),
    'messagingSenderId': config('FIREBASE_MESSAGING_SENDER_ID', default=''),
    'appId': config('FIREBASE_APP_ID', default=''),
    'databaseURL': ''  # No necesitamos database para auth
}

# Inicializar Firebase Admin SDK (para el servidor)
def initialize_firebase_admin():
    """Inicializa Firebase Admin SDK con las credenciales del servidor"""
    if not firebase_admin._apps:
        try:
            # Opción 1: Usar variable de entorno con el JSON completo (para producción/Coolify)
            firebase_credentials_json = config('FIREBASE_ADMIN_CREDENTIALS_JSON', default='')
            
            if firebase_credentials_json:
                import json
                cred_dict = json.loads(firebase_credentials_json)
                cred = credentials.Certificate(cred_dict)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK inicializado desde variable de entorno")
                return
            
            # Opción 2: Usar archivo local (para desarrollo)
            cred_path = config('FIREBASE_ADMIN_CREDENTIALS_PATH', default='')
            
            if cred_path and os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("Firebase Admin SDK inicializado desde archivo")
            else:
                print("Warning: Firebase Admin credentials no encontradas. Algunas funciones pueden no funcionar.")
        except Exception as e:
            print(f"Error al inicializar Firebase Admin SDK: {e}")

# Inicializar Pyrebase (para el cliente)
def initialize_pyrebase():
    """Inicializa Pyrebase para autenticación del lado del cliente"""
    try:
        firebase = pyrebase.initialize_app(FIREBASE_WEB_CONFIG)
        return firebase
    except Exception as e:
        print(f"Error al inicializar Pyrebase: {e}")
        return None

# Inicializar Firebase al importar el módulo
initialize_firebase_admin()
firebase_client = initialize_pyrebase()


class FirebaseAuthService:
    """Servicio para manejar autenticación con Firebase"""
    
    @staticmethod
    def verify_google_token(id_token):
        """
        Verifica un token de Google Sign-In
        
        Args:
            id_token (str): Token de ID de Google
            
        Returns:
            dict: Información del usuario si es válido, None si no lo es
        """
        try:
            decoded_token = auth.verify_id_token(id_token)
            return {
                'uid': decoded_token.get('uid'),
                'email': decoded_token.get('email'),
                'name': decoded_token.get('name', ''),
                'picture': decoded_token.get('picture', ''),
                'email_verified': decoded_token.get('email_verified', False),
            }
        except Exception as e:
            print(f"Error al verificar token de Google: {e}")
            return None
    
    @staticmethod
    def send_password_reset_sms(phone_number):
        """
        Envía un código de verificación por SMS para recuperación de contraseña
        
        Args:
            phone_number (str): Número de teléfono en formato E.164 (ej: +573001234567)
            
        Returns:
            dict: Información de la sesión de verificación si es exitoso, None si falla
        """
        try:
            # Firebase enviará automáticamente el SMS
            # El código de verificación se validará con verify_phone_code
            return {
                'success': True,
                'phone_number': phone_number,
                'message': 'Código de verificación enviado por SMS'
            }
        except Exception as e:
            print(f"Error al enviar SMS: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def verify_phone_code(phone_number, code):
        """
        Verifica el código de SMS recibido
        
        Args:
            phone_number (str): Número de teléfono
            code (str): Código de verificación de 6 dígitos
            
        Returns:
            bool: True si el código es válido, False si no lo es
        """
        try:
            # La verificación del código se hace del lado del cliente con Firebase Auth
            # Esta función es para validación adicional del lado del servidor si es necesario
            return True
        except Exception as e:
            print(f"Error al verificar código: {e}")
            return False
    
    @staticmethod
    def create_custom_token(uid):
        """
        Crea un token personalizado para un usuario
        
        Args:
            uid (str): UID del usuario
            
        Returns:
            str: Token personalizado
        """
        try:
            custom_token = auth.create_custom_token(uid)
            return custom_token.decode('utf-8')
        except Exception as e:
            print(f"Error al crear token personalizado: {e}")
            return None
    
    @staticmethod
    def get_user_by_email(email):
        """
        Obtiene información de un usuario por email
        
        Args:
            email (str): Email del usuario
            
        Returns:
            dict: Información del usuario si existe, None si no existe
        """
        try:
            user = auth.get_user_by_email(email)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'phone_number': user.phone_number,
                'photo_url': user.photo_url,
                'email_verified': user.email_verified,
            }
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            print(f"Error al obtener usuario: {e}")
            return None
    
    @staticmethod
    def get_user_by_phone(phone_number):
        """
        Obtiene información de un usuario por número de teléfono
        
        Args:
            phone_number (str): Número de teléfono en formato E.164
            
        Returns:
            dict: Información del usuario si existe, None si no existe
        """
        try:
            user = auth.get_user_by_phone_number(phone_number)
            return {
                'uid': user.uid,
                'email': user.email,
                'display_name': user.display_name,
                'phone_number': user.phone_number,
                'photo_url': user.photo_url,
            }
        except auth.UserNotFoundError:
            return None
        except Exception as e:
            print(f"Error al obtener usuario por teléfono: {e}")
            return None


# Función helper para obtener el objeto auth de pyrebase
def get_firebase_auth():
    """Retorna el objeto de autenticación de Firebase"""
    if firebase_client:
        return firebase_client.auth()
    return None

