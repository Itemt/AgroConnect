# Variables de Entorno para AgroConnect

## Variables Requeridas para Google OAuth

Agrega estas variables a tu archivo `.env` local y a las variables de entorno de Coolify:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=90070952239-6mibg7a7cvnofgtt3ph4oh54q3ecc0d1.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
```

## Configuración en Coolify

1. Ve a tu proyecto en Coolify
2. Ve a "Environment Variables"
3. Agrega las siguientes variables:

### Variables de Google OAuth:
- `GOOGLE_CLIENT_ID` = `90070952239-6mibg7a7cvnofgtt3ph4oh54q3ecc0d1.apps.googleusercontent.com`
- `GOOGLE_CLIENT_SECRET` = `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`

### Variables de Firebase (ya existentes):
- `FIREBASE_API_KEY` = `AIzaSyBocgWBneNY_ElZDwP7_H3y6Egg1wChF9Q`
- `FIREBASE_AUTH_DOMAIN` = `agroconnect-b9b1c.firebaseapp.com`
- `FIREBASE_PROJECT_ID` = `agroconnect-b9b1c`
- `FIREBASE_STORAGE_BUCKET` = `agroconnect-b9b1c.firebasestorage.app`
- `FIREBASE_MESSAGING_SENDER_ID` = `90070952239`
- `FIREBASE_APP_ID` = `1:90070952239:web:c6486c84288c86f5ddd9da`

## Configuración Local

Agrega las variables de Google OAuth a tu archivo `.env`:

```bash
# Google OAuth Configuration
GOOGLE_CLIENT_ID=90070952239-6mibg7a7cvnofgtt3ph4oh54q3ecc0d1.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=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
```

## Seguridad

⚠️ **IMPORTANTE**: 
- NUNCA subas el `GOOGLE_CLIENT_SECRET` a GitHub
- Estas variables están en `.gitignore` para desarrollo local
- En producción, usa las variables de entorno de Coolify
