# AgroConnect 🌾

> Plataforma web que conecta directamente a productores agrícolas con compradores en Colombia, eliminando intermediarios y facilitando un comercio más justo y transparente.

[![Django](https://img.shields.io/badge/Django-4.2-green.svg)](https://www.djangoproject.com/)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-13%2B-blue.svg)](https://www.postgresql.org/)
[![MercadoPago](https://img.shields.io/badge/MercadoPago-Integrated-00B1EA.svg)](https://www.mercadopago.com.co/)

---

## 📋 Tabla de Contenidos

- [🚀 Características Principales](#-características-principales)
- [🛠 Tecnologías](#-tecnologías)
- [📦 Instalación](#-instalación)
- [⚙️ Configuración](#️-configuración)
- [🏗️ Estructura del Proyecto](#️-estructura-del-proyecto)
- [💳 Sistema de Pagos](#-sistema-de-pagos)
- [🗄️ Estructura de Base de Datos](#️-estructura-de-base-de-datos)
- [🚀 Despliegue](#-despliegue)
- [📝 Licencia](#-licencia)

---

## 🚀 Características Principales

### 👥 **Sistema Multi-Rol de Usuarios**
- **Registro diferenciado**: Productores con fincas y Compradores simples
- **Perfiles personalizados**: `ProducerProfile` y `BuyerProfile` con estadísticas
- **Transición flexible**: Opción "¿Quieres ser vendedor?" para compradores
- **Autenticación robusta**: Sistema completo con recuperación de contraseña

### 🏡 **Gestión Integral de Fincas**
- **Fincas técnicas detalladas**: Ubicación, tipo de suelo, riego, certificaciones
- **Múltiples fincas por productor**: Gestión CRUD completa
- **Trazabilidad completa**: Cada producto vinculado a su finca de origen
- **Información geográfica**: 32 departamentos + 1,100+ municipios colombianos

### 🌾 **Inventario de Cultivos**
- **Estados del cultivo**: Sembrado → Crecimiento → Listo para Cosecha → Cosechado
- **Gestión de áreas**: Control de área ocupada vs disponible por finca
- **Categorización**: Hortalizas, Frutas, Cereales, Leguminosas, Tubérculos, etc.
- **Unidades flexibles**: kg, toneladas, libras, unidades, cajas, bultos, arrobas

### 🛒 **Marketplace Avanzado**
- **Catálogo dinámico**: Grid responsivo con imágenes y badges
- **Búsqueda y filtros**: Por texto, categoría, precio, ubicación, ordenamiento
- **Carrito de compras**: Gestión completa con cálculo automático de totales
- **Publicaciones desde cultivos**: Asociadas a finca específica con trazabilidad

### ⚖️ **Sistema de Conversión de Unidades**
- **Unidades de peso convertibles**: kg, g, libras, arrobas, toneladas (conversión automática)
- **Unidades discretas fijas**: unidades, cajas, bultos (sin conversión)
- **Conversión automática de precios**: El sistema calcula el precio en la unidad elegida por el comprador
- **Validación de disponibilidad**: Previene compras que excedan el stock disponible
- **Flexibilidad para compradores**: Compra en tu unidad preferida aunque el vendedor publique en otra
- **Transparencia para vendedores**: Avisos claros sobre unidades convertibles vs fijas

#### ¿Cómo Funciona?
**Ejemplo práctico:**
- 🌾 **Vendedor publica**: 3 arrobas de tomate a $50,000/arroba
- 🛒 **Comprador quiere**: 5 kg de tomate
- ⚙️ **Sistema convierte**: 
  - 1 arroba = 11.502 kg
  - Precio por kg = $50,000 ÷ 11.502 = $4,346/kg
  - Total por 5 kg = $21,730
  - Disponible: 34.5 kg (3 arrobas convertidas)
- ✅ **Validación automática**: El comprador no puede pedir más de 34.5 kg

**Unidades soportadas:**
- **Convertibles** (peso): Kilogramos (kg), Gramos (g), Libras (lb), Arrobas (@), Toneladas (t)
- **Fijas** (discretas): Unidades, Cajas, Bultos - solo se pueden comprar en la unidad publicada

### 📦 **Sistema Completo de Pedidos**
- **Flujo de estados**: Pendiente → Confirmado → En Preparación → Enviado → En Tránsito → Recibido → Completado
- **Gestión por roles**: Acciones específicas para compradores y vendedores
- **Seguimiento en tiempo real**: Notificaciones automáticas de cambios de estado
- **Cancelación inteligente**: Con devolución automática de stock

### 💳 **Pagos con MercadoPago**
- **Múltiples métodos**: Tarjetas de crédito/débito, PSE, efectivo (Baloto, Efecty)
- **Modo demo universitario**: Simulación automática para pruebas académicas
- **Webhooks configurados**: Confirmación automática de pagos
- **Seguridad completa**: Cumplimiento PCI DSS, no se almacenan datos sensibles

### ⭐ **Sistema de Calificaciones**
- **Calificaciones bidireccionales**: Comprador ↔ Vendedor
- **Multidimensionales**: Calificación general, comunicación, puntualidad, calidad
- **Rankings públicos**: Top productores y compradores
- **Comentarios y recomendaciones**: Sistema de confianza integrado

### 💬 **Mensajería Directa**
- **Chat por publicación**: Conversaciones contextuales
- **Polling simple**: Actualización periódica de mensajes
- **Historial completo**: Todas las conversaciones guardadas
- **API para conversaciones**: Integración fácil con frontend

### 🔔 **Sistema de Notificaciones**
- **Notificaciones automáticas**: Nuevos pedidos, cambios de estado, pagos confirmados
- **Gestión completa**: Marcar como leída, eliminar, filtrar por categoría
- **Estadísticas**: Total, no leídas, leídas
- **Categorías**: Pedido, Pago, Sistema

### 🤖 **Asistente IA (Opcional)**
- **Asistente inteligente**: Consultas generales con Gemini
- **Sugerencias para publicaciones**: Títulos, precios, descripciones optimizadas
- **Contexto colombiano**: Precios en COP, ubicaciones, agricultura local
- **Fallback robusto**: Funciona sin IA con sugerencias predeterminadas

---

## 🛠 Tecnologías

### Backend
- **Django 4.2.24** - Framework web principal
- **Python 3.11+** - Lenguaje de programación
- **PostgreSQL 13+** - Base de datos relacional
- **Gunicorn 21.2.0** - Servidor WSGI para producción

### Pagos y Servicios
- **MercadoPago SDK 2.3.0** - Pasarela de pagos
- **Cloudinary** - Almacenamiento de imágenes en producción
- **Google Gemini** - IA para asistente y sugerencias (opcional)

### Frontend
- **HTML5/CSS3** - Semántica moderna
- **JavaScript (Vanilla)** - Interactividad del lado del cliente
- **Font Awesome 6.4** - Iconografía
- **CSS Personalizado** - Sistema de diseño propio

### Deployment & Storage
- **Docker** - Containerización
- **WhiteNoise 6.7.0** - Servir archivos estáticos en producción
- **dj-database-url** - Configuración de base de datos por URL
- **python-decouple** - Gestión de variables de entorno

### Dependencias Principales
```
Django==4.2.24
psycopg2-binary==2.9.7
mercadopago==2.3.0
django-cloudinary-storage==0.3.0
whitenoise==6.7.0
gunicorn==21.2.0
pillow==11.3.0
dj-database-url==2.1.0
python-decouple==3.8
google-generativeai==0.7.2
Faker==37.8.0
```

---

## 📦 Instalación

### Requisitos Previos
- Python 3.11+
- PostgreSQL 13+
- Git

### 1️⃣ Clonar el Repositorio
```bash
git clone https://github.com/tu-usuario/AgroConnect.git
cd AgroConnect
```

### 2️⃣ Crear Entorno Virtual
```bash
# Crear entorno virtual
python -m venv venv

# Activar en Windows
venv\Scripts\activate

# Activar en macOS/Linux
source venv/bin/activate
```

### 3️⃣ Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# Django Settings
SECRET_KEY=tu_secret_key_super_segura_aqui
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (PostgreSQL)
DATABASE_URL=postgres://usuario:password@localhost:5432/agroconnect

# MercadoPago (Requerido para pagos)
MERCADOPAGO_ACCESS_TOKEN=tu_access_token_aqui

# Cloudinary (Opcional, solo producción)
CLOUDINARY_CLOUD_NAME=tu_cloud_name
CLOUDINARY_API_KEY=tu_api_key
CLOUDINARY_API_SECRET=tu_api_secret

# Google Gemini (Opcional, para IA)
GOOGLE_API_KEY=tu_google_api_key
# o alternativamente:
GEMINI_API_KEY=tu_gemini_api_key

# Configuración Regional
LANGUAGE_CODE=es-es
TIME_ZONE=America/Bogota
```

### 5️⃣ Configurar Base de Datos

**Crear base de datos PostgreSQL:**
```bash
# Conectar a PostgreSQL
psql -U postgres

# Crear base de datos
CREATE DATABASE agroconnect;
CREATE USER agroconnect_user WITH PASSWORD 'tu_password';
GRANT ALL PRIVILEGES ON DATABASE agroconnect TO agroconnect_user;
\q
```

**Ejecutar migraciones:**
```bash
python manage.py migrate
```

### 6️⃣ Crear Superusuario
```bash
python manage.py createsuperuser
```

### 7️⃣ Cargar Datos de Prueba (Opcional)
```bash
python manage.py seed_data
```

### 8️⃣ Ejecutar Servidor de Desarrollo
```bash
python manage.py runserver
```

🎉 **¡Listo!** La aplicación estará disponible en `http://127.0.0.1:8000/`

---

## ⚙️ Configuración

### Variables de Entorno Detalladas

| Variable | Requerida | Descripción | Ejemplo |
|----------|-----------|-------------|---------|
| `SECRET_KEY` | ✅ | Llave secreta de Django | `django-insecure-abc123...` |
| `DEBUG` | ✅ | Modo de depuración | `True` / `False` |
| `ALLOWED_HOSTS` | ✅ | Hosts permitidos (separados por coma) | `localhost,midominio.com` |
| `DATABASE_URL` | ✅ | URL de conexión PostgreSQL | `postgres://user:pass@host:5432/db` |
| `MERCADOPAGO_ACCESS_TOKEN` | ⚠️ | Token de MercadoPago | `APP_USR-...` |
| `CLOUDINARY_CLOUD_NAME` | ❌ | Nombre de Cloudinary (prod) | `mi-cloud` |
| `CLOUDINARY_API_KEY` | ❌ | API Key de Cloudinary (prod) | `123456789` |
| `CLOUDINARY_API_SECRET` | ❌ | Secret de Cloudinary (prod) | `abc123...` |
| `GOOGLE_API_KEY` | ❌ | API Key de Google Gemini (IA) | `AIza...` |

**Leyenda:** ✅ Obligatorio | ⚠️ Requerido para funcionalidad específica | ❌ Opcional

### Configuración de MercadoPago

#### 1. Obtener Credenciales

1. Regístrate en [MercadoPago Developers](https://www.mercadopago.com.co/developers)
2. Ve a "Tus aplicaciones" → "Crear aplicación"
3. Obtén tus credenciales:
   - **Access Token de Producción**: Para pagos reales
   - **Access Token de Prueba**: Para desarrollo y testing

#### 2. Configurar Webhooks

En el panel de MercadoPago:
1. Ve a "Webhooks"
2. Agrega tu URL: `https://tu-dominio.com/payments/notification/`
3. Selecciona eventos: `payment`, `merchant_order`

#### 3. Modo Demo (Proyecto Universitario)

Si no tienes credenciales o fallan, el sistema simula pagos automáticamente:
- ✅ Se crea el pedido
- ✅ Se marca como pagado
- ✅ El vendedor puede confirmar y procesar
- ⚠️ **Solo para demos académicas, no usar en producción real**

---

## 🏗️ Estructura del Proyecto

```
AgroConnect/
│
├── 📁 accounts/              # Sistema de usuarios y autenticación
│   ├── models.py            # User, Farm, ProducerProfile, BuyerProfile
│   ├── views.py             # Registro, login, perfiles, admin dashboard
│   ├── forms.py             # Formularios de usuario
│   └── ajax_views.py        # Vistas AJAX para ciudades/departamentos
│
├── 📁 core/                  # Funcionalidades compartidas
│   ├── models.py            # BaseModel, Notification, Farm (técnica)
│   ├── views.py             # Notificaciones, asistente IA, sugerencias
│   ├── colombia_locations.py # Base de datos de ubicaciones
│   └── urls.py              # URLs de APIs core
│
├── 📁 inventory/             # Gestión de inventario (productores)
│   ├── models.py            # Crop (cultivos)
│   ├── views.py             # CRUD cultivos, dashboard productor
│   └── forms.py             # Formularios de cultivos
│
├── 📁 marketplace/           # Marketplace y publicaciones
│   ├── models.py            # Publication (con sistema de conversión de unidades)
│   ├── views.py             # Listado, búsqueda, filtros, CRUD publicaciones
│   └── forms.py             # Formularios de publicaciones
│
├── 📁 cart/                  # Carrito de compras
│   ├── models.py            # Cart, CartItem
│   ├── views.py             # Añadir, eliminar, actualizar carrito
│   └── context_processors.py # Carrito en contexto global
│
├── 📁 sales/                 # Pedidos, mensajería y calificaciones
│   ├── models.py            # Order, Conversation, Message, Rating
│   ├── views.py             # Flujo completo de pedidos, chat, ratings
│   └── forms.py             # Formularios de pedidos y calificaciones
│
├── 📁 payments/              # Sistema de pagos MercadoPago
│   ├── models.py            # Payment
│   ├── views.py             # Checkout, webhooks, confirmaciones
│   ├── mercadopago_service.py # Servicio de integración MercadoPago
│   └── urls.py              # URLs de pagos
│
├── 📁 templates/             # Plantillas HTML
│   ├── base.html            # Template base
│   ├── index.html           # Página de inicio
│   ├── accounts/            # Templates de autenticación
│   ├── marketplace/         # Templates del marketplace
│   ├── inventory/           # Templates de inventario
│   ├── sales/               # Templates de pedidos y chat
│   ├── payments/            # Templates de pagos
│   └── core/                # Templates de notificaciones
│
├── 📁 static/                # Archivos estáticos
│   ├── css/                 # Estilos CSS personalizados
│   ├── js/                  # JavaScript vanilla
│   └── images/              # Imágenes y assets
│
├── 📁 media/                 # Archivos de usuarios (desarrollo)
│   ├── crops/               # Imágenes de cultivos
│   └── publications/        # Imágenes de publicaciones
│
├── 📁 agroconnect/           # Configuración del proyecto
│   ├── settings.py          # Configuración Django
│   ├── urls.py              # URLs principales
│   ├── wsgi.py              # WSGI para deployment
│   └── asgi.py              # ASGI (WebSockets - comentado)
│
├── 📄 Dockerfile             # Configuración Docker
├── 📄 requirements.txt       # Dependencias Python
├── 📄 manage.py              # CLI de Django
└── 📄 README.md              # Este archivo
```

---

## 💳 Sistema de Pagos

### Flujo de Pago

```mermaid
graph LR
    A[Comprador crea pedido] --> B[Ir a pagar]
    B --> C{¿MercadoPago configurado?}
    C -->|Sí| D[Crear preferencia de pago]
    C -->|No| E[Simular pago automático]
    D --> F[Redirigir a MercadoPago]
    F --> G{¿Pago exitoso?}
    G -->|Sí| H[Webhook confirma pago]
    G -->|No| E
    E --> I[Pago aprobado automáticamente]
    H --> I
    I --> J[Pedido en estado 'pendiente']
    J --> K[Vendedor confirma pedido]
    K --> L[Proceso de envío]
```

### Endpoints de Pagos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/payments/checkout/<order_id>/` | Iniciar proceso de pago |
| `GET` | `/payments/success/` | Página de pago exitoso |
| `GET` | `/payments/failure/` | Página de pago fallido |
| `GET` | `/payments/pending/` | Página de pago pendiente |
| `POST` | `/payments/notification/` | Webhook de MercadoPago |
| `POST` | `/payments/confirmation/` | Confirmación de pago |
| `GET` | `/payments/history/` | Historial de pagos |
| `GET` | `/payments/<payment_id>/` | Detalle de pago específico |

### Estados de Pago

- **`pending`**: Pago pendiente de confirmación
- **`approved`**: Pago aprobado y confirmado
- **`rejected`**: Pago rechazado por MercadoPago
- **`failed`**: Pago fallido por error técnico
- **`cancelled`**: Pago cancelado por el usuario
- **`in_process`**: Pago en proceso de verificación
- **`in_mediation`**: Pago en mediación

### Métodos de Pago Soportados

| Método | Logo | Disponibilidad |
|--------|------|----------------|
| Tarjetas de Crédito/Débito | 💳 | Visa, MasterCard, AmEx, Diners |
| PSE | 🏦 | Transferencia bancaria online |
| Efectivo | 💵 | Baloto, Efecty, Gana, etc. |

---

## 🗄️ Estructura de Base de Datos

### Diagrama Entidad-Relación Simplificado

```
┌─────────────────┐       ┌──────────────────┐
│   User (Auth)   │───────│ ProducerProfile  │
│                 │       │  BuyerProfile    │
└────────┬────────┘       └──────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐       ┌──────────────────┐
│   Farm (Core)   │───────│  Crop (Inventory)│
│                 │  1:N  │                  │
└─────────────────┘       └────────┬─────────┘
                                   │
                                   │ 1:N
                                   ▼
                          ┌──────────────────┐
                          │   Publication    │
                          │  (Marketplace)   │
                          └────────┬─────────┘
                                   │
                                   │ 1:N
                                   ▼
         ┌─────────────────────────┴─────────┐
         │                                   │
         ▼                                   ▼
┌──────────────────┐              ┌──────────────────┐
│  Order (Sales)   │──────1:1─────│ Payment (Pagos)  │
└────────┬─────────┘              └──────────────────┘
         │
         │ 1:N
         ▼
┌──────────────────┐
│ Rating (Calific.)│
└──────────────────┘
```

### Modelos Principales

#### 👤 **accounts.User**
```python
- username, email, password (heredado de AbstractUser)
- role: 'Productor' | 'Comprador'
- cedula: str (único)
- telefono: str
- departamento, ciudad: str
- can_sell: bool (permisos de venta)
- profile_image: ImageField
```

#### 🏡 **core.Farm** (Finca Técnica)
```python
- nombre: str
- propietario: FK → User
- departamento, ciudad, direccion: str
- coordenadas_lat, coordenadas_lng: Decimal
- area_total, area_cultivable: Decimal
- tipo_suelo: choices (arcilloso, arenoso, limoso, etc.)
- tipo_riego: choices (natural, goteo, aspersión, etc.)
- certificacion_organica, certificacion_bpa: bool
- activa: bool
```

#### 🌾 **inventory.Crop** (Cultivo)
```python
- nombre: str
- categoria: choices (hortalizas, frutas, cereales, etc.)
- productor: FK → User
- finca: FK → Farm
- area_ocupada: Decimal
- cantidad_estimada: Decimal
- unidad_medida: choices (kg, toneladas, libras, etc.)
- estado: choices (sembrado, en_crecimiento, listo_para_cosechar, cosechado)
- fecha_disponibilidad: Date
- notas: text
```

#### 📢 **marketplace.Publication** (Publicación)
```python
- cultivo: FK → Crop
- finca: FK → Farm
- precio_por_unidad: Decimal
- cantidad_disponible: Decimal (con conversión de unidades)
- cantidad_minima: Decimal
- unidad_medida: choices (kg, g, libras, arrobas, toneladas, unidades, cajas, bultos)
- departamento, ciudad: str
- categoria: choices
- estado: choices (Activa, Pausada, Agotada)
- descripcion: text
- imagen: ImageField

# Métodos de conversión de unidades:
- convertir_unidad(cantidad, unidad_origen, unidad_destino)
- obtener_precio_en_unidad(unidad_destino)
- es_unidad_convertible()
- verificar_disponibilidad(cantidad_solicitada, unidad_solicitada)
```

#### 🛒 **cart.Cart** y **cart.CartItem**
```python
# Cart
- user: OneToOne → User
- created_at: DateTime

# CartItem
- cart: FK → Cart
- publication: FK → Publication
- quantity: Decimal (soporta decimales para conversiones)
- unidad_compra: str (unidad elegida por el comprador)

# Propiedades calculadas:
- get_item_price() - calcula el precio con conversión de unidades
- precio_unitario_display() - precio por unidad en la unidad de compra
```

#### 📦 **sales.Order** (Pedido)
```python
- publicacion: FK → Publication
- comprador: FK → User
- cantidad_acordada: Decimal
- precio_total: Decimal
- estado: choices (pendiente, confirmado, en_preparacion, enviado, 
                   en_transito, recibido, completado, cancelado)
- notas_comprador, notas_vendedor: text
- direccion_entrega: text
- fecha_confirmacion, fecha_envio, fecha_entrega_estimada, fecha_recepcion: DateTime
```

#### ⭐ **sales.Rating** (Calificación)
```python
- pedido: FK → Order
- calificador: FK → User
- calificado: FK → User
- tipo: choices (comprador_a_vendedor, vendedor_a_comprador)
- calificacion_general: Int (1-5)
- calificacion_comunicacion: Int (1-5)
- calificacion_puntualidad: Int (1-5)
- calificacion_calidad: Int (1-5)
- comentario: text
- recomendaria: bool
```

#### 💳 **payments.Payment** (Pago)
```python
- order: OneToOne → Order
- user: FK → User
- mercadopago_id: str (único)
- preference_id: str
- external_reference: str
- amount: Decimal
- currency: str (default='COP')
- payment_method: choices (pse, credit_card, debit_card, cash)
- status: choices (pending, approved, rejected, failed, cancelled)
- description: text
- response_data: JSONField
- paid_at: DateTime
```

#### 🔔 **core.Notification** (Notificación)
```python
- recipient: FK → User
- title: str
- message: text
- category: choices (order, payment, system)
- is_read: bool
- read_at: DateTime
- order_id, payment_id: Int (opcional)
```

---

## 🚀 Despliegue

### Despliegue con Docker (Coolify)

#### 1. Preparar Variables de Entorno

En el panel de Coolify, configura:

```env
SECRET_KEY=tu_secret_key_super_segura
DEBUG=False
ALLOWED_HOSTS=tu-dominio.com,www.tu-dominio.com

DATABASE_URL=postgres://usuario:password@host:5432/agroconnect

CLOUDINARY_CLOUD_NAME=tu_cloud
CLOUDINARY_API_KEY=tu_key
CLOUDINARY_API_SECRET=tu_secret

MERCADOPAGO_ACCESS_TOKEN=tu_access_token

GOOGLE_API_KEY=tu_gemini_key

LANGUAGE_CODE=es-es
TIME_ZONE=America/Bogota
```

#### 2. Conectar Repositorio

1. En Coolify → "New Resource" → "Application"
2. Conecta tu repositorio Git
3. Branch: `main`
4. Build Pack: Dockerfile (se detecta automáticamente)

#### 3. Configurar Dominio

1. En Coolify → "Domains"
2. Agrega tu dominio personalizado
3. SSL se configura automáticamente con Let's Encrypt

#### 4. Deploy

Click en "Deploy" y Coolify:
- Construye la imagen Docker
- Ejecuta `collectstatic`
- Inicia Gunicorn en puerto 8000

#### 5. Ejecutar Migraciones

En la terminal de Coolify:
```bash
python manage.py migrate
```

#### 6. Crear Superusuario

```bash
python manage.py createsuperuser
```

### Comandos Útiles en Producción

```bash
# Ver logs en tiempo real
docker logs -f container_name

# Reiniciar aplicación
# (En Coolify: Click en "Restart")

# Ejecutar comando en el contenedor
docker exec -it container_name python manage.py comando

# Backup de base de datos
pg_dump -h host -U user agroconnect > backup.sql

# Restaurar base de datos
psql -h host -U user agroconnect < backup.sql
```

---

## 📊 Endpoints API Principales

### Autenticación
- `POST /accounts/register/` - Registro de usuarios
- `POST /accounts/login/` - Inicio de sesión
- `POST /accounts/logout/` - Cierre de sesión

### Marketplace
- `GET /marketplace/` - Listado de publicaciones
- `GET /publication/<id>/` - Detalle de publicación
- `POST /publication/new/` - Crear publicación

### Pedidos
- `POST /order/new/<publication_id>/` - Crear pedido
- `GET /order/<id>/` - Detalle de pedido
- `POST /order/<id>/update/` - Actualizar estado
- `GET /order/history/` - Historial de pedidos

### Carrito
- `POST /cart/add/<publication_id>/` - Añadir al carrito
- `POST /cart/remove/<item_id>/` - Eliminar del carrito
- `POST /cart/update/<item_id>/` - Actualizar cantidad
- `GET /cart/` - Ver carrito

### Notificaciones
- `GET /core/notifications/` - Listar notificaciones
- `POST /core/notifications/mark-read/` - Marcar como leída
- `POST /core/notifications/mark-all-read/` - Marcar todas como leídas

### IA (Opcional)
- `POST /assistant/reply/` - Asistente IA
- `POST /ai/suggestions/` - Sugerencias para publicaciones

---

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Para contribuir:

1. **Fork** el repositorio
2. Crea una **rama** para tu feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. **Push** a la rama (`git push origin feature/AmazingFeature`)
5. Abre un **Pull Request**

### Guías de Contribución

- Sigue PEP 8 para código Python
- Escribe tests para nuevas funcionalidades
- Actualiza la documentación según sea necesario
- Usa commits descriptivos y en español

---

## 🐛 Reporte de Bugs

Si encuentras un bug, por favor:

1. Verifica que no esté ya reportado en Issues
2. Crea un nuevo Issue con:
   - Descripción clara del problema
   - Pasos para reproducir
   - Comportamiento esperado vs actual
   - Screenshots si aplica
   - Información del entorno (OS, Python version, etc.)

---

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver archivo `LICENSE` para más detalles.

---

## 👥 Autores

**Cristian Ramos** & **Jhonnier Arguello**

- GitHub: [@Itemt](https://github.com/Itemt)
- Proyecto: [AgroConnect](https://github.com/Itemt/AgroConnect)

---

## 📧 Contacto

¿Tienes preguntas o sugerencias? No dudes en contactarnos:

- 📧 Email: contacto@agroconnect.com
- 🌐 Website: [agroconnect.itemt.tech](https://agroconnect.itemt.tech)
- 💬 Issues: [GitHub Issues](https://github.com/Itemt/AgroConnect/issues)

---

<div align="center">

**AgroConnect** - Conectando el campo con la ciudad 🌾🏙️

*Desarrollado con ❤️ en Colombia*

[![GitHub stars](https://img.shields.io/github/stars/Itemt/AgroConnect?style=social)](https://github.com/Itemt/AgroConnect/stargazers)
[![GitHub forks](https://img.shields.io/github/forks/Itemt/AgroConnect?style=social)](https://github.com/Itemt/AgroConnect/network/members)

</div>
