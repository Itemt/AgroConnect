/**
 * Firebase Phone Authentication Helper
 * Maneja el envío de OTP por SMS usando Firebase Authentication
 */
class FirebasePhoneAuthHelper {
    constructor() {
        this.recaptchaVerifier = null;
        this.confirmationResult = null;
        this.phoneNumber = null;
    }

    /**
     * Inicializa Firebase Phone Auth
     */
    initialize() {
        try {
            // Verificar que Firebase esté disponible
            if (typeof firebase === 'undefined') {
                console.error('Firebase no está cargado');
                return false;
            }

            // Configurar reCAPTCHA para SMS
            this.setupRecaptcha();
            return true;
        } catch (error) {
            console.error('Error inicializando Firebase Phone Auth:', error);
            return false;
        }
    }

    /**
     * Configura reCAPTCHA para el envío de SMS
     */
    setupRecaptcha() {
        try {
            // Crear reCAPTCHA invisible
            this.recaptchaVerifier = new firebase.auth.RecaptchaVerifier('recaptcha-container', {
                'size': 'invisible',
                'callback': (response) => {
                    console.log('reCAPTCHA resuelto');
                },
                'expired-callback': () => {
                    console.log('reCAPTCHA expirado');
                }
            });
        } catch (error) {
            console.error('Error configurando reCAPTCHA:', error);
        }
    }

    /**
     * Envía código OTP por SMS
     */
    async sendOTP(phoneNumber) {
        try {
            if (!this.recaptchaVerifier) {
                throw new Error('reCAPTCHA no configurado');
            }

            // Limpiar número de teléfono
            const cleanPhone = this.cleanPhoneNumber(phoneNumber);
            if (!cleanPhone) {
                throw new Error('Número de teléfono inválido');
            }

            this.phoneNumber = cleanPhone;

            // Enviar código de verificación
            this.confirmationResult = await firebase.auth().signInWithPhoneNumber(cleanPhone, this.recaptchaVerifier);
            
            console.log('Código OTP enviado a:', cleanPhone);
            return {
                success: true,
                message: 'Código enviado correctamente'
            };

        } catch (error) {
            console.error('Error enviando OTP:', error);
            return {
                success: false,
                message: this.getErrorMessage(error.code)
            };
        }
    }

    /**
     * Verifica el código OTP
     */
    async verifyOTP(otpCode) {
        try {
            if (!this.confirmationResult) {
                throw new Error('No hay verificación en proceso');
            }

            const result = await this.confirmationResult.confirm(otpCode);
            console.log('Código OTP verificado correctamente');
            
            return {
                success: true,
                user: result.user,
                message: 'Código verificado correctamente'
            };

        } catch (error) {
            console.error('Error verificando OTP:', error);
            return {
                success: false,
                message: this.getErrorMessage(error.code)
            };
        }
    }

    /**
     * Limpia y valida el número de teléfono
     */
    cleanPhoneNumber(phoneNumber) {
        if (!phoneNumber) return null;
        
        // Remover caracteres no numéricos
        const clean = phoneNumber.replace(/\D/g, '');
        
        // Si empieza con 57 (Colombia), mantenerlo
        if (clean.startsWith('57') && clean.length === 12) {
            return `+${clean}`;
        }
        
        // Si empieza con 3 y tiene 10 dígitos, agregar código de país
        if (clean.startsWith('3') && clean.length === 10) {
            return `+57${clean}`;
        }
        
        // Si ya tiene formato internacional
        if (clean.startsWith('57') && clean.length >= 10) {
            return `+${clean}`;
        }
        
        return null;
    }

    /**
     * Convierte códigos de error de Firebase a mensajes legibles
     */
    getErrorMessage(errorCode) {
        const errorMessages = {
            'auth/invalid-phone-number': 'Número de teléfono inválido',
            'auth/too-many-requests': 'Demasiados intentos. Intenta más tarde',
            'auth/quota-exceeded': 'Límite de SMS excedido',
            'auth/captcha-check-failed': 'Error de verificación reCAPTCHA',
            'auth/invalid-verification-code': 'Código de verificación inválido',
            'auth/code-expired': 'Código expirado',
            'auth/invalid-verification-id': 'ID de verificación inválido',
            'auth/missing-phone-number': 'Número de teléfono requerido',
            'auth/network-request-failed': 'Error de conexión. Verifica tu internet'
        };

        return errorMessages[errorCode] || 'Error desconocido. Intenta nuevamente';
    }

    /**
     * Limpia recursos
     */
    cleanup() {
        if (this.recaptchaVerifier) {
            this.recaptchaVerifier.clear();
            this.recaptchaVerifier = null;
        }
        this.confirmationResult = null;
        this.phoneNumber = null;
    }
}

// Instancia global
window.firebasePhoneAuth = new FirebasePhoneAuthHelper();
