/**
 * Firebase Authentication Helper
 * Funciones para manejar Google Sign-In usando OAuth directo
 */

class FirebaseAuthHelper {
    constructor() {
        // Solo el Client ID es necesario en el frontend
        this.clientId = window.GOOGLE_CLIENT_ID || '';
        if (!this.clientId) {
            throw new Error('Google OAuth Client ID not configured');
        }
    }

    /**
     * Inicializar Google Sign-In usando redirect (evita infinite loop)
     */
    async signInWithGoogleRedirect() {
        try {
            console.log('=== INICIANDO GOOGLE SIGN-IN (REDIRECT) ===');
            
            const redirectUri = encodeURIComponent(window.location.origin + '/auth/google-callback/');
            console.log('🔗 Nueva URI de redirección:', redirectUri);
            const scope = encodeURIComponent('openid profile email');
            const state = 'google-signin-' + Date.now();
            
                const googleAuthUrl = `https://accounts.google.com/o/oauth2/auth?` +
                    `client_id=${this.clientId}&` +
                    `redirect_uri=${redirectUri}&` +
                    `scope=${scope}&` +
                    `response_type=code&` +
                    `state=${state}&` +
                    `prompt=select_account`;
                
                console.log('🔗 URL de Google OAuth:', googleAuthUrl);
                console.log('🌐 Redirect URI:', redirectUri);
                console.log('🌐 Preparando redirección...');
            
            // Redirigir directamente (evita infinite loop)
            console.log('🌐 Redirigiendo a Google...');
            window.location.href = googleAuthUrl;
            
        } catch (error) {
            console.error('❌ Error en Google Sign-In:', error);
            throw error;
        }
    }

    /**
     * Verificar si hay código de autorización en la URL
     */
    async checkAuthCode() {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');
        
        console.log('🔍 Verificando código de autorización...');
        console.log('URL params:', {
            code: code ? code.substring(0, 20) + '...' : 'No encontrado',
            state: state || 'No encontrado',
            error: error || 'No encontrado'
        });
        
        if (error) {
            throw new Error(`Error de Google OAuth: ${error}`);
        }
        
        if (code && state) {
            console.log('✅ Código de autorización encontrado!');
            console.log('Code:', code.substring(0, 20) + '...');
            console.log('State:', state);
            
            // Dejar que el backend haga el intercambio con el client_secret
            return { code };
        }
        
        // Si no hay código, no es un error - solo significa que la página se cargó normalmente
        console.log('ℹ️ No hay código de autorización - página cargada normalmente');
        return null;
    }

    /**
     * Intercambiar código por token
     */
    async exchangeCodeForToken() { /* ya no se usa en frontend */ }

    /**
     * Obtener información del usuario usando el access token
     */
    async getUserInfo(accessToken) {
        console.log('👤 Obteniendo información del usuario...');
        
        try {
            const response = await fetch('https://www.googleapis.com/oauth2/v2/userinfo', {
                headers: {
                    'Authorization': `Bearer ${accessToken}`
                }
            });
            
            const userInfo = await response.json();
            
            if (userInfo.email) {
                console.log('✅ Información del usuario obtenida:', userInfo);
                return userInfo;
            } else {
                throw new Error('No se pudo obtener información del usuario');
            }
        } catch (error) {
            console.error('❌ Error obteniendo información del usuario:', error);
            throw error;
        }
    }

    /**
     * Procesar el login del usuario
     */
    async processUserLogin(userInfo) {
        console.log('🔄 Procesando login del usuario...');
        
        try {
            // Mostrar mensaje de carga
            this.showLoadingMessage('Procesando login...');
            
            // Obtener el CSRF token
            const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                             document.querySelector('meta[name=csrf-token]')?.getAttribute('content');
            
            if (!csrfToken) {
                throw new Error('No se encontró el CSRF token');
            }
            
            console.log('CSRF Token:', csrfToken ? 'Found' : 'Not found');
            
            // Enviar información del usuario al servidor
            const response = await fetch('/accounts/google-signin/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    userInfo: userInfo
                })
            });
            
            console.log('Response status:', response.status);
            const data = await response.json();
            console.log('Server response:', data);
            
            this.hideLoadingMessage();
            
            if (data.success) {
                console.log('✅ Login exitoso! Redirecting to:', data.redirect_url);
                window.location.href = data.redirect_url;
            } else {
                throw new Error(data.error || 'Error desconocido del servidor');
            }
            
        } catch (error) {
            console.error('❌ Error procesando login:', error);
            this.hideLoadingMessage();
            alert('Error al procesar el login: ' + error.message);
            throw error;
        }
    }

    /**
     * Mostrar mensaje de carga
     */
    showLoadingMessage(message) {
        const loadingDiv = document.createElement('div');
        loadingDiv.id = 'firebase-loading';
        loadingDiv.className = 'fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50';
        loadingDiv.innerHTML = `
            <div class="bg-white p-6 rounded-lg shadow-xl text-center">
                <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto mb-4"></div>
                <span class="text-lg">${message}</span>
            </div>
        `;
        document.body.appendChild(loadingDiv);
    }

    /**
     * Ocultar mensaje de carga
     */
    hideLoadingMessage() {
        const loadingDiv = document.getElementById('firebase-loading');
        if (loadingDiv) {
            loadingDiv.remove();
        }
    }

    /**
     * Método principal para iniciar el proceso de login
     */
    async startGoogleSignIn() {
        try {
            // El redirect no retorna, simplemente redirige
            await this.signInWithGoogleRedirect();
        } catch (error) {
            console.error('❌ Error en Google Sign-In:', error);
            alert('Error al iniciar sesión con Google: ' + error.message);
        }
    }
}

// Crear instancia global
window.FirebaseAuthHelper = FirebaseAuthHelper;
