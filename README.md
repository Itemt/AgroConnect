# AgroConnect 🌾

AgroConnect es una plataforma web desarrollada con Django que conecta directamente a productores agrícolas con compradores, eliminando intermediarios y facilitando un comercio más justo y eficiente en Colombia.

## 🚀 Características Principales

### 👥 Sistema de Usuarios Multi-Rol
- **Roles diferenciados:** Productores, Compradores y Administradores con funcionalidades específicas.
- **Autenticación segura:** Sistema de registro e inicio de sesión con validación.
- **Perfiles detallados:** 
  - Información de contacto completa (teléfono, WhatsApp)
  - Ubicación por departamento y ciudad de Colombia
  - Imágenes de perfil personalizables
  - Información de negocio (para productores)
- **Dashboard personalizado** según el rol del usuario.

### 🏡 Sistema de Gestión de Fincas
- **Gestión completa de fincas:**
  - Registro de fincas con información detallada
  - Ubicación específica (departamento/ciudad con dropdown dinámico)
  - Características del suelo y tipo de riego
  - Área total, cultivable y ocupada
  - Certificaciones (orgánica, BPA, otras)
- **Registro de productores con finca inicial:**
  - Al registrarse como productor, se crea automáticamente su primera finca
  - Formulario unificado que incluye datos personales + finca
  - Mensaje informativo: "Si quieres agregar más fincas, puedes hacerlo desde tu perfil"
- **Panel principal de gestión:**
  - "Mis Fincas" como punto central de gestión
  - Vista detallada de cada finca con cultivos asociados
  - CRUD completo para fincas
  - Estadísticas de área disponible vs ocupada

### 🌾 Gestión de Inventario Orientada a Fincas
- **Cultivos asociados a fincas:**
  - Cada cultivo se asocia a una finca específica
  - Área ocupada por cultivo en la finca
  - Validación de área disponible vs ocupada
- **Estados de cultivo:** 
  - Siembra → Crecimiento → Listo para Cosecha → Cosechado
- **Dashboard del productor:**
  - Resumen de fincas y cultivos
  - Ingresos totales y pendientes
  - Estadísticas de ventas por producto
  - Pedidos recientes y que requieren atención
- **Publicaciones con origen de finca:**
  - Las publicaciones muestran la finca de origen
  - Filtros por finca en el marketplace
  - Trazabilidad completa desde finca hasta comprador

### 🔔 Sistema de Notificaciones en Tiempo Real
- **Notificaciones automáticas:**
  - Nuevos pedidos para productores
  - Cambios de estado de pedidos para compradores
  - Confirmaciones de pago
  - Cancelaciones y actualizaciones
- **Panel de notificaciones:**
  - Bell icon con badge de notificaciones no leídas
  - Dropdown con notificaciones recientes
  - Página dedicada con historial completo
  - Estadísticas: total, no leídas, leídas
- **Gestión de notificaciones:**
  - Marcar como leída individual
  - Marcar todas como leídas/no leídas
  - Filtros por categoría (pedido, pago, sistema)
- **WebSockets:** Actualización en tiempo real con Django Channels

### 🛒 Marketplace y Carrito de Compras
- **Catálogo de productos dinámico:**
  - Grid responsivo de productos con imágenes
  - Badges de categoría y precio
  - Vista detallada de cada publicación con información de finca
- **Búsqueda y filtros avanzados:**
  - Búsqueda por texto (productos, productores, descripciones)
  - Filtro por categoría
  - Filtro por rango de precio
  - Filtro por ubicación (ciudad/región)
  - Ordenamiento: más reciente, precio menor/mayor, nombre A-Z
- **Carrito de compras funcional:**
  - Añadir productos con validación de cantidad mínima
  - Modificar cantidades directamente
  - Eliminar artículos
  - Cálculo automático de totales
  - Resumen completo del pedido
- **Gestión de publicaciones:**
  - Crear publicaciones desde cultivos listos
  - Seleccionar finca de origen
  - Editar precio, cantidad, descripción e imagen
  - Estados: Activa, Vendida, Inactiva

### 📦 Sistema de Pedidos Avanzado
- **Flujo completo de pedidos:**
  - Pendiente → Confirmado → En Preparación → Enviado → En Tránsito → Entregado → Completado
- **Gestión por roles:**
  - **Compradores:** 
    - Realizar pedidos desde el marketplace
    - Seguimiento de estado en tiempo real
    - Confirmar recepción de productos
    - Calificar vendedores después de la entrega
  - **Productores:** 
    - Confirmar o rechazar pedidos
    - Actualizar estados de envío
    - Gestionar entregas
    - Ver historial completo de ventas
- **Funcionalidades especiales:**
  - Cancelación de pedidos con devolución automática de stock
  - Validación de cantidades disponibles
  - Cálculo automático de totales
  - Historial completo de todos los pedidos
- **Vista detallada de pedidos:**
  - Información del producto y vendedor/comprador
  - Estado actual y timeline de progreso
  - Botones de acción según el estado y rol

### 💳 Sistema de Pagos con MercadoPago
- **Integración completa con MercadoPago:**
  - Pasarela de pagos líder en Latinoamérica
  - Procesamiento seguro de transacciones
  - Webhooks para confirmación automática de pagos
- **Métodos de pago soportados:**
  - 💳 Tarjetas de Crédito y Débito (Visa, MasterCard, AmEx)
  - 🏦 PSE (Transferencia bancaria en línea)
  - 💵 Efectivo (Baloto, Efecty, Gana, etc.)
  - 🏪 Transferencias bancarias
- **Funcionalidades:**
  - Checkout seguro con formulario de MercadoPago
  - Referencias únicas por transacción
  - Historial completo de pagos
  - Estados de pago en tiempo real
  - Validación de montos mínimos ($1,000 COP)
  - Modo de prueba para desarrollo
- **Seguridad:**
  - No se almacenan datos sensibles de tarjetas
  - Todas las transacciones usan HTTPS
  - Verificación de webhooks
  - Cumplimiento con estándares PCI DSS

### ⭐ Sistema de Calificaciones y Rankings
- **Calificaciones multidimensionales:**
  - Calificación general (1-5 estrellas)
  - Comunicación
  - Puntualidad en la entrega
  - Calidad del producto
- **Rankings públicos:**
  - Top productores por calificación
  - Top compradores por actividad
  - Estadísticas de ventas totales
  - Número de calificaciones recibidas
- **Sistema de recomendaciones:**
  - Comentarios detallados
  - Indicador de "Recomendarías al vendedor"
  - Historial de calificaciones dadas y recibidas
- **Cálculo automático:** Promedios actualizados en tiempo real.

### 💬 Sistema de Mensajería en Tiempo Real
- **Chat bidireccional:**
  - Comunicación directa entre compradores y productores
  - Interfaz de chat moderna y responsiva
  - Mensajes organizados por conversación
- **Conversaciones por publicación:**
  - Cada producto tiene su hilo de conversación
  - Contexto del producto siempre visible
  - Acceso rápido al producto desde el chat
- **Gestión de conversaciones:**
  - Lista de todas las conversaciones activas
  - Indicadores de mensajes nuevos
  - Búsqueda de conversaciones
  - Historial completo de mensajes
- **WebSockets:** Actualización en tiempo real con Django Channels.

### 🤖 Inteligencia Artificial Integrada

#### Asistente IA Flotante
- **Burbuja flotante** disponible en todas las páginas
- **Dos pestañas principales:**
  - **"Asistente"**: Consultas generales con respuestas elaboradas usando Gemini Pro
  - **"Chats"**: Mini chat para conversaciones activas sin salir del marketplace
- **Características técnicas:**
  - Integración con Google Gemini Pro (`gemini-1.5-flash`)
  - Rate limiting de 2 segundos entre consultas
  - Respuestas de hasta 800 tokens con markdown completo
  - Fallback inteligente cuando la IA no está disponible
  - Soporte para preguntas generales y específicas de agricultura

#### Sugerencias de IA para Publicaciones
- **Sistema inteligente** que optimiza publicaciones de cultivos:
  - **Títulos sugeridos** atractivos y descriptivos
  - **Precios recomendados** basados en mercado colombiano
  - **Descripciones profesionales** que resaltan calidad
  - **Tips de marketing** específicos para Colombia
- **Integración perfecta:**
  - Botón "Sugerencias IA" en formularios de publicación
  - Modal elegante con loading y contenido dinámico
  - Aplicación directa de sugerencias a campos del formulario
  - Rate limit de 3 segundos entre sugerencias
- **Optimización de tokens:**
  - 400 tokens máximo por sugerencia
  - Prompt optimizado para respuestas concisas
  - Fallback robusto si la IA no está disponible

#### Gestión de Conversaciones Inteligente
- **Conversaciones activas**: Solo conversaciones con actividad en los últimos 15 días
- **Conversaciones archivadas**: Indicador de cantidad con link al panel completo
- **Reactivación automática**: Al enviar mensaje en conversación antigua, se reactiva
- **Endpoints especializados:**
  - `GET /api/conversations/` → conversaciones activas + contador de archivadas
  - `POST /assistant/reply/` → respuestas del asistente IA
  - `POST /ai/suggestions/` → sugerencias para publicaciones

### 📊 Analytics y Estadísticas Detalladas

#### Dashboard del Productor:
- **Métricas financieras:**
  - Ingresos totales generados
  - Ingresos pendientes de cobro
  - Gráficos de tendencias de ventas
- **Análisis de fincas:**
  - Resumen de todas las fincas
  - Área total vs cultivable vs ocupada
  - Cultivos por finca
- **Análisis de productos:**
  - Top 5 productos más vendidos
  - Estadísticas por categoría
  - Inventario actual
- **Análisis de clientes:**
  - Top compradores frecuentes
  - Total de clientes únicos
  - Patrones de compra
- **Gestión de pedidos:**
  - Pedidos pendientes de atención
  - Pedidos en progreso
  - Historial completo
- **Reputación:**
  - Calificación promedio
  - Calificaciones recientes
  - Comentarios de compradores

#### Dashboard del Comprador:
- **Resumen de compras:**
  - Total gastado
  - Número de pedidos realizados
  - Pedidos activos
- **Productos favoritos:**
  - Productos más comprados
  - Productores favoritos
- **Historial:**
  - Pedidos completados
  - Pedidos pendientes
  - Calificaciones dadas

### 🗺️ Sistema de Ubicación para Colombia
- **Base de datos completa:**
  - 32 departamentos
  - Más de 1,100 municipios y ciudades
- **Selección en cascada:**
  - Seleccionar departamento
  - Automáticamente se cargan las ciudades de ese departamento
  - Implementado con AJAX para mejor UX
- **Filtros geográficos:**
  - Buscar productos por ubicación
  - Ver productores cercanos

## 🛠 Tecnologías Utilizadas

### Backend
- **Python 3.9+**
- **Django 4.2** - Framework web principal
- **Django Channels** - WebSockets para chat y notificaciones en tiempo real
- **Pillow** - Procesamiento de imágenes
- **MercadoPago SDK** - Integración con pasarela de pagos

### Frontend
- **HTML5 / CSS3** con semántica moderna
- **TailwindCSS** - Framework CSS con configuración personalizada
- **CSS personalizado** - Variables CSS, gradientes y animaciones
- **JavaScript (Vanilla)** - Interactividad avanzada del lado del cliente
- **Font Awesome 6.4** - Iconografía completa
- **Google Fonts (Inter)** - Tipografía moderna y legible

### Base de Datos
- **PostgreSQL** - Producción
- **SQLite** - Desarrollo

### Deployment & Storage
- **Coolify** - Plataforma de deployment self-hosted
- **Digital Ocean** - Infraestructura (Droplets)
- **Docker** - Containerización en producción
- **Git** - Control de versiones
- **Cloudinary** - Almacenamiento de imágenes en producción
- **WhiteNoise** - Servir archivos estáticos en producción

### Librerías Python Principales
```
Django==4.2.16
channels==4.1.0
pillow==11.0.0
psycopg2-binary==2.9.10
faker==33.1.0
mercadopago==2.3.0
django-cloudinary-storage==0.3.0
cloudinary==1.44.1
whitenoise==6.8.2
widget-tweaks==1.4.12
google-generativeai==0.7.1
python-decouple==3.8
```

## 📋 Instalación y Configuración

### Opción 1: Desarrollo Local

#### 1. Clonar el Repositorio
```bash
git clone https://github.com/Itemt/AgroConnect.git
cd AgroConnect
```

#### 2. Crear y Activar Entorno Virtual
```bash
# Crear el entorno virtual
python -m venv venv

# Activar en macOS/Linux
source venv/bin/activate

# Activar en Windows
venv\Scripts\activate
```

#### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

#### 4. Configurar Variables de Entorno (Opcional)
Para desarrollo local, Django usará SQLite por defecto. Para PostgreSQL y otras configuraciones:
```bash
# Crear archivo .env en la raíz del proyecto

# Base de Datos (opcional, si usas PostgreSQL localmente)
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=agroconnect
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_contraseña

# Cloudinary (opcional, solo si quieres usar Cloudinary en desarrollo)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# MercadoPago (requerido para funcionalidad de pagos)
MERCADOPAGO_ACCESS_TOKEN=tu_access_token

# Gemini (opcional, para el asistente)
GOOGLE_API_KEY=tu_clave
# o
GEMINI_API_KEY=tu_clave
```

### 🤖 Asistente IA y Mini Chat Integrado

- **Burbuja flotante** en todas las páginas con dos pestañas:
  - **"Asistente"**: respuestas elaboradas usando Gemini (`gemini-1.5-flash`) cuando `GOOGLE_API_KEY` está configurada; si no, fallback inteligente.
  - **"Chats"**: lista de conversaciones activas y un hilo compacto para seguir conversando sin salir del marketplace.
- **Optimización de tokens**: entrada limitada, `max_output_tokens=800`, markdown completo y respuestas detalladas.
- **Conversaciones activas y archivadas**:
  - La pestaña "Chats" muestra solo conversaciones con actividad en los últimos 15 días.
  - Si hay conversaciones antiguas, se indica la cantidad como "archivadas" con link al panel completo (`/conversations/`).
  - Al enviar un mensaje en una conversación antigua desde el panel completo, se re-activa y vuelve a aparecer como reciente.
- **Diseño mejorado**:
  - Ventana más grande y cómoda para mejor experiencia de usuario
  - Layout de dos columnas: lista de conversaciones (izquierda) + chat activo (derecha)
  - Búsqueda en tiempo real para filtrar conversaciones
  - Título dinámico del chat seleccionado
- **Endpoints relevantes**:
  - `GET /api/conversations/` → conversaciones activas (≤15 días) + `archived_count`.
  - `GET /conversation/<id>/messages/?since=<lastId>` → polling de nuevos mensajes.
  - `POST /conversation/<id>/` (AJAX) → enviar mensaje.
  - `POST /assistant/reply/` → respuestas del asistente IA.

### 🧠 Sugerencias de IA para Publicaciones

- **Sistema inteligente** que optimiza publicaciones de cultivos usando IA:
  - **Títulos sugeridos** atractivos y descriptivos
  - **Precios recomendados** basados en mercado colombiano con explicaciones
  - **Descripciones profesionales** que resaltan calidad y origen
  - **Tips de marketing** específicos para Colombia
- **Integración perfecta**:
  - Botón "Sugerencias IA" en el formulario de publicación
  - Modal elegante con loading y contenido dinámico
  - Aplicación directa de sugerencias a campos del formulario
  - Rate limit de 3 segundos entre sugerencias
- **Optimización de tokens**:
  - `max_output_tokens=400` por sugerencia
  - Prompt optimizado para respuestas concisas pero útiles
  - Fallback robusto si la IA no está disponible
- **Endpoint**: `POST /ai/suggestions/` → genera sugerencias basadas en datos del cultivo

### 💳 Sistema de Pagos con MercadoPago

- **Integración completa** con MercadoPago para procesamiento de pagos:
  - **Múltiples métodos de pago**: PSE, tarjetas de crédito/débito, Efecty
  - **Configuración automática** de datos del pagador para evitar botones deshabilitados
  - **URLs de retorno** configuradas para flujo completo de pago
  - **Webhooks** para confirmación automática de pagos
- **Procesamiento inteligente**:
  - **Modo sandbox** para desarrollo y pruebas
  - **Procesamiento automático** para proyectos universitarios
  - **Fallback robusto** si MercadoPago no está disponible
  - **Debug logging** para identificar problemas de integración
- **Configuración segura**:
  - Variables de entorno para tokens de acceso
  - Limpieza automática de información sensible
  - Validación de datos del pagador
  - Manejo de errores mejorado
- **Endpoints de pago**:
  - `POST /payments/checkout/` → crear preferencia de pago
  - `GET /payments/success/` → confirmación de pago exitoso
  - `POST /payments/notification/` → webhook de MercadoPago
  - `GET /payments/failure/` → manejo de pagos fallidos

### Clave de Gemini en Producción (Coolify)

1. En Coolify → tu aplicación → Settings → Environment Variables.
2. Agrega `GOOGLE_API_KEY` con tu clave de Google AI Studio.
3. Guarda y Deploy/Restart para reconstruir e inyectar la variable en el contenedor.
4. Seguridad: no publiques tu clave en el repositorio ni en el README.

## 📸 Capturas y GIFs del Asistente y Mini Chat

Agrega estas imágenes/GIFs en `static/images/docs/` (crea la carpeta si no existe) y actualiza los nombres si lo prefieres. Luego se mostrarán aquí automáticamente.

```markdown
![Burbuja del Asistente](static/images/docs/assistant-bubble.png)
![Pestaña Asistente (respuesta IA)](static/images/docs/assistant-tab-ai.gif)
![Pestaña Chats (mini chat en cualquier página)](static/images/docs/assistant-tab-chats.gif)
```

Sugerencias para grabar GIFs
- Windows: Xbox Game Bar (Win+G) para video + `ezgif.com` para convertir a GIF.
- macOS: QuickTime para video + `gifcap.dev` o `Gifski`.
- Linux: `peek` o `obs-studio` + conversión con `ffmpeg`/`ezgif`.

#### 5. Aplicar Migraciones
```bash
python manage.py migrate
```

#### 6. Crear Superusuario
```bash
python manage.py createsuperuser
```

#### 7. Generar Datos de Prueba (Opcional)
```bash
# Poblar con datos de ejemplo
python manage.py seed_data
```

#### 8. Ejecutar el Servidor
```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/`

### Opción 2: Deploy con Coolify en Digital Ocean (Producción)

#### Prerequisitos
- Droplet de Digital Ocean con Coolify instalado
- PostgreSQL database configurado (puede ser managed o en el mismo droplet)

#### Configuración en Coolify

1. **Crear nuevo proyecto en Coolify:**
   - Accede a tu panel de Coolify
   - Click en "New Resource" → "Application"
   - Selecciona "Public Repository" o "Private Repository"

2. **Conecta tu repositorio:**
   - URL del repositorio: `https://github.com/tu-usuario/AgroConnect.git`
   - Branch: `main`
   - Build Pack: Dockerfile (Coolify detectará el Dockerfile automáticamente)

3. **Configura Variables de Entorno:**
   
   En la sección "Environment Variables" de tu aplicación en Coolify:

   **Base de Datos (PostgreSQL):**
   ```
   POSTGRES_HOST=tu_host_postgres
   POSTGRES_PORT=5432
   POSTGRES_DB=agroconnect
   POSTGRES_USER=tu_usuario
   POSTGRES_PASSWORD=tu_password
   ```

   **Cloudinary (para imágenes en producción):**
   ```
   CLOUDINARY_CLOUD_NAME=tu_cloud_name
   CLOUDINARY_API_KEY=tu_api_key
   CLOUDINARY_API_SECRET=tu_api_secret
   ```

   **MercadoPago (para pagos):**
   ```
   MERCADOPAGO_ACCESS_TOKEN=tu_access_token
   ```

   **Google Gemini (para IA):**
   ```
   GOOGLE_API_KEY=tu_clave_de_google_ai_studio
   # o alternativamente:
   GEMINI_API_KEY=tu_clave_de_google_ai_studio
   ```

   **Configuración Django:**
   ```
   DEBUG=False
   SECRET_KEY=tu_secret_key_super_segura_aqui
   ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com
   ```

4. **Configurar dominio (opcional):**
   - En Coolify, ve a "Domains"
   - Agrega tu dominio personalizado
   - Coolify configurará SSL automáticamente con Let's Encrypt

5. **Deploy:**
   - Click en "Deploy"
   - Coolify construirá la imagen Docker y la desplegará
   - Tu app estará disponible en el dominio configurado

#### Crear Usuario Administrador en Producción

**Usando la terminal de Coolify:**
```bash
# En Coolify, ve a tu aplicación → "Terminal" y ejecuta:
python manage.py shell
```

Luego en el shell de Python:
```python
from accounts.models import User
admin = User.objects.create_superuser(
    username='admin',
    email='admin@agroconnect.com',
    password='tu_password_seguro',
    role='administrador',
    first_name='Admin',
    last_name='AgroConnect'
)
exit()
```

**Eliminar Usuario Administrador:**
```python
# En la terminal de Coolify:
python manage.py shell

from accounts.models import User
User.objects.filter(username='admin', role='administrador').delete()
exit()
```

#### Comandos Útiles en Coolify

**Ver logs en tiempo real:**
- En Coolify, ve a tu aplicación → "Logs"
- O usa la terminal y ejecuta: `docker logs -f nombre_contenedor`

**Reiniciar la aplicación:**
- Click en "Restart" en el panel de Coolify
- O redeploy: Click en "Deploy" nuevamente

**Ejecutar migraciones manualmente:**
```bash
# En la terminal de Coolify:
python manage.py migrate
```

**Recolectar archivos estáticos:**
```bash
# En la terminal de Coolify:
python manage.py collectstatic --noinput
```

#### Troubleshooting

**Si las imágenes no cargan:**
1. Verifica que las variables de Cloudinary estén configuradas
2. Revisa los logs: `docker logs nombre_contenedor`
3. Asegúrate que `DEFAULT_FILE_STORAGE` esté configurado en `settings.py`

**Si la base de datos no conecta:**
1. Verifica las variables de entorno de PostgreSQL
2. Asegúrate que el host de PostgreSQL sea accesible desde el contenedor
3. Si PostgreSQL está en el mismo droplet, usa la IP interna

**Si el deployment falla:**
1. Revisa los logs de build en Coolify
2. Verifica que el `Dockerfile` sea correcto
3. Asegúrate que `requirements.txt` tenga todas las dependencias

**Configurar webhook de ePayco (IMPORTANTE):**
1. Ve al [dashboard de ePayco](https://dashboard.epayco.co/)
2. Ve a "Configuración" → "URLs de Confirmación"
3. Agrega tu URL de confirmación: `https://tu-dominio.com/payments/confirmation/`
4. Esta URL debe ser accesible públicamente para que ePayco envíe las confirmaciones de pago
5. Para probar localmente, puedes usar [ngrok](https://ngrok.com/) o [localtunnel](https://localtunnel.github.io/www/)

## 💳 Configuración Detallada de ePayco

### Obtener Credenciales

1. **Registrarse en ePayco:**
   - Ve a [ePayco](https://www.epayco.co/) y crea una cuenta
   - Completa el proceso de verificación de tu negocio

2. **Obtener llaves de API:**
   - Accede al [dashboard de ePayco](https://dashboard.epayco.co/)
   - Ve a "Integraciones" en el menú lateral
   - Encontrarás tus llaves:
     - **Public Key (P_CUST_ID_XXXXXXXX)**: Llave pública para el frontend
     - **Private Key**: Llave privada para el backend (¡NO la compartas!)

3. **Configurar URLs de confirmación:**
   - En el dashboard, ve a "Configuración" → "URLs de Confirmación"
   - **URL de Respuesta:** `https://tu-dominio.com/payments/success/`
   - **URL de Confirmación (Webhook):** `https://tu-dominio.com/payments/confirmation/`

### Modo de Prueba

Para desarrollo, ePayco ofrece un modo de prueba:
- Usa tus credenciales normales
- Activa `EPAYCO_TEST_MODE=True`
- Usa tarjetas de prueba:
  - **Visa:** 4575623182290326
  - **MasterCard:** 5254133511684471
  - **CVV:** 123
  - **Fecha:** Cualquier fecha futura
  - **Cuotas:** 1

### Métodos de Pago Disponibles

- **Tarjetas de Crédito:** Visa, MasterCard, American Express, Diners
- **PSE:** Transferencias bancarias en línea
- **Efectivo:** Baloto, Efecty, Gana, etc.

### Comisiones

ePayco cobra comisiones por transacción. Consulta las tarifas actuales en su sitio web.

## 🗂️ Estructura del Proyecto

```
AgroConnect/
├── accounts/           # Gestión de usuarios y perfiles
│   ├── models.py      # User, ProducerProfile, BuyerProfile
│   ├── views.py       # Autenticación, registro, perfiles
│   ├── forms.py       # Formularios de usuario
│   └── forms_farm.py  # Formularios extendidos con fincas
├── core/              # Funcionalidades compartidas
│   ├── models.py      # Notification, Farm, BaseModel
│   ├── views.py       # Notificaciones, APIs
│   ├── views_farm.py  # CRUD de fincas
│   ├── forms.py       # Formularios de fincas
│   ├── consumers.py   # WebSocket para notificaciones
│   ├── routing.py     # Rutas de WebSockets
│   └── colombia_locations.py  # Base de datos de ubicaciones
├── inventory/         # Gestión de cultivos (productores)
│   ├── models.py      # Crop (con relación a Farm)
│   ├── views.py       # CRUD de cultivos, dashboard
│   └── forms.py       # Formularios de cultivos
├── marketplace/       # Marketplace y publicaciones
│   ├── models.py      # Publication (con relación a Farm)
│   ├── views.py       # Listado, búsqueda, filtros
│   └── forms.py       # Formularios de publicaciones
├── cart/              # Carrito de compras
│   ├── models.py      # Cart, CartItem
│   └── views.py       # Gestión del carrito
├── sales/             # Pedidos, mensajería y calificaciones
│   ├── models.py      # Order, Conversation, Message, Rating
│   ├── views.py       # Flujo de pedidos, calificaciones
│   ├── consumers.py   # WebSocket handlers para chat
│   └── routing.py     # Rutas de WebSockets
├── payments/          # Sistema de pagos con ePayco
│   ├── models.py      # Payment
│   ├── views.py       # Checkout, confirmaciones, webhooks
│   ├── epayco_service.py  # Servicio de integración ePayco
│   └── README.md      # Documentación específica de pagos
├── templates/         # Plantillas HTML
│   ├── base.html      # Template base con navegación mejorada
│   ├── index.html     # Página de inicio renovada
│   ├── accounts/      # Templates de autenticación
│   │   └── register_producer.html  # Registro específico de productores
│   ├── core/          # Templates de notificaciones y fincas
│   │   ├── notifications.html
│   │   ├── farm_list.html
│   │   ├── farm_form.html
│   │   ├── farm_detail.html
│   │   └── farm_confirm_delete.html
│   ├── marketplace/   # Templates del marketplace
│   └── sales/         # Templates de pedidos y dashboards
├── static/            # Archivos estáticos (CSS, JS, imágenes)
│   ├── css/           # Estilos personalizados
│   │   └── custom.css # Sistema de diseño completo
│   ├── js/            # JavaScript personalizado
│   │   ├── main.js    # Funcionalidades principales
│   │   └── enhanced-ui.js # Interactividad mejorada
│   └── images/        # Imágenes y assets
├── agroconnect/       # Configuración del proyecto
│   ├── settings.py    # Configuración de Django
│   ├── urls.py        # Rutas principales
│   └── asgi.py        # Configuración ASGI para WebSockets
├── Dockerfile         # Configuración de Docker
├── requirements.txt   # Dependencias Python
└── manage.py          # CLI de Django
```

## 🔄 Flujo de Trabajo Típico

### Para un Productor:
1. **Registrarse** como productor con información de negocio, ubicación y finca inicial
2. **Gestionar fincas** desde "Mis Fincas" (agregar más fincas desde el perfil)
3. **Crear cultivos** asociados a fincas específicas con área ocupada
4. **Actualizar estado** de cultivos conforme crecen
5. **Publicar productos** cuando estén listos para venta (seleccionando finca de origen)
6. **Recibir notificaciones** de nuevos pedidos en tiempo real
7. **Recibir y gestionar pedidos** de compradores
8. **Actualizar estados de envío** (preparación → enviado → entregado)
9. **Recibir calificaciones** y construir reputación
10. **Analizar métricas** de ventas en el dashboard
11. **Comunicarse** con compradores vía chat en tiempo real

### Para un Comprador:
1. **Registrarse** como comprador con información de contacto
2. **Explorar el marketplace** con filtros avanzados
3. **Ver detalles** de productos y perfiles de productores
4. **Ver información de fincas** de origen de los productos
5. **Añadir productos** al carrito con cantidades deseadas
6. **Contactar productores** para negociar detalles
7. **Realizar pedido** desde el carrito
8. **Pagar con MercadoPago** usando tarjeta, PSE o efectivo
9. **Recibir notificaciones** de cambios de estado en tiempo real
10. **Seguir el estado** del pedido y pago en tiempo real
11. **Confirmar recepción** cuando el producto llegue
12. **Calificar al productor** y dejar comentarios
13. **Ver historial** de compras, pagos y gastos totales

### Para un Administrador:
1. **Gestionar usuarios** (crear, editar, eliminar)
2. **Moderar publicaciones** y contenido
3. **Revisar pedidos** y resolver disputas
4. **Monitorear estadísticas** generales de la plataforma
5. **Gestionar categorías** y configuraciones
6. **Ver notificaciones** del sistema

## 📱 Características de UX/UI

### 🎨 Diseño Moderno y Atractivo
- ✨ **Sistema de diseño completo** con TailwindCSS personalizado
- 🎭 **Gradientes y efectos visuales** modernos
- 🎯 **Tipografía Inter** para mejor legibilidad
- 🌈 **Paleta de colores expandida** (primary, secondary, accent)
- 💫 **Animaciones suaves** y micro-interacciones
- 🎪 **Efectos hover** y transiciones elegantes

### 📱 Experiencia de Usuario
- 📱 **Totalmente responsivo** (móvil, tablet, desktop)
- 🎨 **Interfaz intuitiva** con iconografía Font Awesome
- ⚡ **Carga rápida** con optimización de assets
- 🔔 **Notificaciones visuales** para acciones del usuario
- 💬 **Chat en tiempo real** sin necesidad de recargar
- 🔍 **Búsqueda instantánea** con sugerencias
- ✅ **Validación de formularios** en tiempo real
- 🖼️ **Optimización de imágenes** automática
- 🏡 **Gestión visual de fincas** con mapas y estadísticas

### 🎨 Componentes Mejorados
- 🃏 **Tarjetas modernas** con sombras sofisticadas
- 🔘 **Botones con gradientes** y efectos ripple
- 📝 **Formularios elegantes** con labels flotantes
- 🧭 **Navegación mejorada** con backdrop blur
- 🏠 **Hero sections** con patrones decorativos
- 📊 **Dashboards visuales** con estadísticas atractivas
- 🔔 **Panel de notificaciones** con animaciones suaves
- 🏡 **Vistas de fincas** con información detallada

## 🔐 Seguridad

- 🔒 **Autenticación robusta** con Django Auth
- 🛡️ **Protección CSRF** en todos los formularios
- 🚫 **Validación de permisos** por rol
- 🔑 **Contraseñas hasheadas** con algoritmos seguros
- 📝 **Sanitización de inputs** para prevenir XSS
- 🌐 **Protección contra SQL injection** con ORM de Django
- 🔐 **Variables de entorno** para datos sensibles
- 🔔 **Notificaciones seguras** con validación de usuarios

## 🎨 Mejoras de Diseño Implementadas

### ✨ Renovación Visual Completa
- **Sistema de CSS personalizado** con variables CSS y utilidades modernas
- **Configuración TailwindCSS expandida** con colores, sombras y animaciones personalizadas
- **Tipografía Inter** para mejor legibilidad y aspecto profesional
- **Gradientes modernos** en botones, tarjetas y fondos
- **Efectos de profundidad** con sombras multicapa

### 🎭 Componentes Rediseñados
- **Navegación elegante** con logo con gradiente y menú con backdrop blur
- **Tarjetas sofisticadas** con efectos hover 3D y transiciones suaves
- **Botones modernos** con gradientes, efectos ripple y estados de carga
- **Formularios mejorados** con labels flotantes e iconos descriptivos
- **Hero sections** con patrones decorativos y animaciones
- **Panel de notificaciones** con diseño moderno y animaciones

### 🚀 Interactividad Mejorada
- **JavaScript personalizado** para micro-interacciones
- **Animaciones de entrada** para elementos que aparecen en pantalla
- **Efectos hover** en todos los componentes interactivos
- **Navegación inteligente** que se oculta al hacer scroll
- **Estados de carga** dinámicos para operaciones asíncronas
- **WebSockets** para actualizaciones en tiempo real

### 📱 Responsive Design Avanzado
- **Breakpoints optimizados** para todos los dispositivos
- **Navegación móvil** rediseñada con mejor UX
- **Tarjetas adaptables** que se ajustan perfectamente
- **Tipografía escalable** que mantiene legibilidad en todos los tamaños
- **Gestión de fincas** optimizada para móviles

## 🚀 Funcionalidades Implementadas y Futuras

### ✅ Implementadas
- [x] **Sistema de pagos con MercadoPago** (tarjetas, PSE, efectivo) con procesamiento automático
- [x] **Asistente IA integrado** con Gemini Pro para consultas generales y agrícolas
- [x] **Mini chat flotante** con diseño de dos columnas y búsqueda en tiempo real
- [x] **Sugerencias de IA** para optimizar publicaciones de cultivos
- [x] Chat en tiempo real con WebSockets
- [x] Sistema de calificaciones y rankings
- [x] Gestión completa de inventario orientada a fincas
- [x] Marketplace con filtros avanzados
- [x] Panel administrativo completo (CRUD)
- [x] Almacenamiento de imágenes con Cloudinary
- [x] Sistema de ubicaciones de Colombia
- [x] Sistema de notificaciones en tiempo real
- [x] Gestión completa de fincas
- [x] Registro de productores con finca inicial
- [x] Trazabilidad desde finca hasta comprador
- [x] **Sistema de rate limiting** para control de tokens
- [x] **Fallback inteligente** cuando la IA no está disponible

### 🔜 Próximas Funcionalidades
- [ ] Notificaciones push y por email
- [ ] API REST con Django REST Framework
- [ ] Aplicación móvil nativa (React Native / Flutter)

## 🔒 Mejoras de Seguridad Implementadas

### 🛡️ Protección de Información Sensible
- **Limpieza completa** de tokens y API keys del repositorio
- **Variables de entorno** para todas las credenciales sensibles
- **Historial de Git** limpiado de información confidencial
- **Archivos .env** agregados al .gitignore
- **Placeholders seguros** en lugar de tokens reales

### 🔐 Configuración Segura
- **MercadoPago** configurado con variables de entorno
- **Google Gemini** con API key protegida
- **Cloudinary** con credenciales en variables de entorno
- **Base de datos** con configuración segura
- **Debug logging** sin exposición de datos sensibles

### 🚫 Archivos Eliminados
- Comandos de management con tokens hardcodeados
- Archivos de prueba con credenciales reales
- Referencias a servicios descontinuados (ePayco)
- Logs y archivos temporales con información sensible
- [ ] Integración con APIs climáticas
- [ ] Programa de fidelización para compradores
- [ ] Sistema de cupones y descuentos
- [ ] Mapa interactivo de fincas
- [ ] Sistema de certificaciones por finca

## 📊 Modelos de Datos Principales

### User (Django AbstractUser)
- Roles: productor, comprador, administrador
- Información de contacto y perfil

### Farm (Finca)
- Nombre, descripción, ubicación (departamento/ciudad)
- Área total, cultivable y ocupada
- Tipo de suelo y riego
- Certificaciones (orgánica, BPA, otras)
- Relación con productor
- Estado activo/inactivo

### Crop (Cultivo)
- Nombre, categoría, cantidad, unidad
- Estado: siembra → crecimiento → listo → cosechado
- Ubicación y fecha de disponibilidad
- Relación con productor y finca
- Área ocupada en la finca

### Publication (Publicación)
- Relación con cultivo y finca
- Precio, cantidad disponible, cantidad mínima
- Estado: Activa, Vendida, Inactiva
- Imagen y descripción

### Notification (Notificación)
- Destinatario, título, mensaje
- Categoría: pedido, pago, sistema
- Estado leído/no leído
- Relación opcional con pedido/pago
- Timestamps de creación y lectura

### Order (Pedido)
- Relación con publicación, comprador, vendedor
- Cantidad, precio total
- Estado: 7 estados diferentes
- Timestamps de cada cambio de estado

### Payment (Pago)
- Relación con orden y usuario
- Referencia única de ePayco
- Monto y método de pago
- Estado: pending, approved, rejected, failed, cancelled
- Datos de respuesta de ePayco (JSON)

### Rating (Calificación)
- Calificación general + 3 aspectos específicos
- Comentario y recomendación
- Relación con pedido

### Conversation y Message
- Conversaciones por publicación
- Mensajes entre comprador y productor
- Timestamps y estado de lectura

## 🤝 Contribución

Las contribuciones son bienvenidas. Para contribuir:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

## 📧 Contacto

Proyecto desarrollado por Cristian Ramos y Jhonnier Arguello - [GitHub](https://github.com/Itemt/AgroConnect)

---

**AgroConnect** - Conectando el campo con la ciudad 🌾🏙️