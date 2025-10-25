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

            console.log('Firebase está disponible, inicializando Phone Auth...');
            
            // Verificar configuración de Firebase
            if (!firebase.apps.length) {
                console.error('Firebase no está inicializado');
                return false;
            }

            // Configurar reCAPTCHA para SMS
            this.setupRecaptcha();
            console.log('Firebase Phone Auth inicializado correctamente');
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
            // Verificar que el contenedor de reCAPTCHA existe
            const recaptchaContainer = document.getElementById('recaptcha-container');
            if (!recaptchaContainer) {
                console.error('Contenedor de reCAPTCHA no encontrado');
                return;
            }

            console.log('Configurando reCAPTCHA...');
            
            // Crear reCAPTCHA invisible
            this.recaptchaVerifier = new firebase.auth.RecaptchaVerifier('recaptcha-container', {
                'size': 'invisible',
                'callback': (response) => {
                    console.log('reCAPTCHA resuelto correctamente');
                },
                'expired-callback': () => {
                    console.log('reCAPTCHA expirado, reiniciando...');
                    this.recaptchaVerifier = null;
                    this.setupRecaptcha();
                }
            });

            console.log('reCAPTCHA configurado correctamente');
        } catch (error) {
            console.error('Error configurando reCAPTCHA:', error);
            this.recaptchaVerifier = null;
        }
    }

    /**
     * Envía código OTP por SMS
     */
    async sendOTP(phoneNumber) {
        try {
            console.log('Iniciando envío de OTP para:', phoneNumber);
            
            if (!this.recaptchaVerifier) {
                console.error('reCAPTCHA no configurado, intentando configurar...');
                this.setupRecaptcha();
                if (!this.recaptchaVerifier) {
                    throw new Error('No se pudo configurar reCAPTCHA');
                }
            }

            // Limpiar número de teléfono
            const cleanPhone = this.cleanPhoneNumber(phoneNumber);
            if (!cleanPhone) {
                throw new Error('Número de teléfono inválido');
            }

            console.log('Número de teléfono limpio:', cleanPhone);
            this.phoneNumber = cleanPhone;

            // Verificar que Firebase Auth esté disponible
            if (!firebase.auth) {
                throw new Error('Firebase Auth no está disponible');
            }

            console.log('Enviando código de verificación...');
            
            // Enviar código de verificación
            this.confirmationResult = await firebase.auth().signInWithPhoneNumber(cleanPhone, this.recaptchaVerifier);
            
            console.log('Código OTP enviado exitosamente a:', cleanPhone);
            return {
                success: true,
                message: 'Código enviado correctamente'
            };

        } catch (error) {
            console.error('Error detallado enviando OTP:', error);
            console.error('Código de error:', error.code);
            console.error('Mensaje de error:', error.message);
            
            return {
                success: false,
                message: this.getErrorMessage(error.code) || error.message || 'Error desconocido. Intenta nuevamente'
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
        
        console.log('Limpiando número de teléfono:', phoneNumber);
        
        // Remover caracteres no numéricos excepto +
        let clean = phoneNumber.replace(/[^\d+]/g, '');
        
        // Si ya tiene +, mantenerlo
        if (clean.startsWith('+')) {
            console.log('Número ya tiene formato internacional:', clean);
            return clean;
        }
        
        // Si empieza con 57 (Colombia), agregar +
        if (clean.startsWith('57') && clean.length === 12) {
            const result = `+${clean}`;
            console.log('Número colombiano formateado:', result);
            return result;
        }
        
        // Si empieza con 3 y tiene 10 dígitos, agregar código de país colombiano
        if (clean.startsWith('3') && clean.length === 10) {
            const result = `+57${clean}`;
            console.log('Número colombiano con código agregado:', result);
            return result;
        }
        
        // Si tiene 10-15 dígitos, asumir que es un número local y agregar +57
        if (clean.length >= 10 && clean.length <= 15) {
            const result = `+57${clean}`;
            console.log('Número local formateado como colombiano:', result);
            return result;
        }
        
        console.error('Número de teléfono inválido:', phoneNumber, '->', clean);
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
