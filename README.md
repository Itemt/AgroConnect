# AgroConnect

Plataforma web en Django para conectar productores agrícolas con compradores en Colombia. Soporta gestión de fincas, cultivos, publicaciones, carrito, pedidos, pagos (MercadoPago), calificaciones, notificaciones y un asistente/IA para sugerencias.

## Tecnologías

- Backend: Django 4.2
- Base de datos: PostgreSQL (desarrollo y producción) mediante `DATABASE_URL` y `dj-database-url`
- Almacenamiento de imágenes: Cloudinary (solo producción)
- Estáticos: WhiteNoise (producción)
- Pagos: MercadoPago SDK
- Frontend: HTML/CSS/JS (vanilla) + CSS personalizado
- Despliegue: Docker + Gunicorn (ejemplo con Coolify)

## Funcionalidades principales

- Usuarios y perfiles
  - Registro/Login con `accounts.User` (rol: Productor/Comprador)
  - Perfiles `ProducerProfile` y `BuyerProfile`
  - Opción "¿Quieres ser vendedor?" para compradores
- Fincas y cultivos
  - `core.Farm` (finca técnica) y `accounts.Farm` (finca simple para perfiles)
  - `inventory.Crop` asociado a finca, estado, cantidad/unidad, área ocupada
- Marketplace y carrito
  - `marketplace.Publication` desde un `Crop`
  - `cart.Cart` y `cart.CartItem`
- Pedidos, chat, calificaciones, notificaciones
  - `sales.Order`, `Conversation`, `Message`, `Rating`
  - `core.Notification`
- Pagos con MercadoPago
  - `payments.Payment`
  - Servicio `payments/mercadopago_service.py`
  - Vistas y webhooks reales
  - Modo demo: auto-aprobación simulada para pruebas universitarias si falla o no hay credenciales
- Asistente y Sugerencias IA
  - Endpoints en `core.views` para asistente y sugerencias en publicaciones (Gemini opcional)

## Requisitos

- Python 3.11
- PostgreSQL 13+ accesible y un `DATABASE_URL` válido

## Variables de entorno

Configurar como variables del entorno del sistema o archivo `.env` (usado por `python-decouple`):

- SECRET_KEY
- DEBUG=false|true
- ALLOWED_HOSTS=dominio1,dominio2 (lista separada por comas)
- DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DB
- CLOUDINARY_CLOUD_NAME (prod)
- CLOUDINARY_API_KEY (prod)
- CLOUDINARY_API_SECRET (prod)
- MERCADOPAGO_ACCESS_TOKEN (requerido para pagos reales)
- GOOGLE_API_KEY o GEMINI_API_KEY (opcional, para IA)

## Instalación (desarrollo)

1) Crear entorno y dependencias
```bash
python -m venv venv
venv\Scripts\activate   # Windows
# source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

2) Configurar base de datos PostgreSQL
- Crear la base y configurar `DATABASE_URL` (no se usa SQLite por defecto en este proyecto)

3) Migraciones y datos
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py seed_data  # opcional
```

4) Ejecutar
```bash
python manage.py runserver
```

La app estará en `http://127.0.0.1:8000/`.

## Configuración relevante (settings)

- Base de datos: `DATABASES['default'] = dj_database_url.config(default=config('DATABASE_URL'), conn_max_age=600)`
- Archivos estáticos: WhiteNoise habilitado
- Media: local en desarrollo; Cloudinary en producción (`DEFAULT_FILE_STORAGE`)
- Usuario custom: `AUTH_USER_MODEL = 'accounts.User'`
- Pagos: `MERCADOPAGO_ACCESS_TOKEN` requerido para uso real

## Pagos (MercadoPago)

- Servicio: `payments/mercadopago_service.py`
- URLs (`payments/urls.py`):
  - `POST /payments/checkout/<order_id>/` (UI/crea preferencia o simula)
  - `GET  /payments/success/`
  - `GET  /payments/failure/`
  - `GET  /payments/pending/`
  - `POST /payments/confirmation/` (webhook compatible)
  - `POST /payments/notification/` (webhook de notificaciones)
- Modo demo universitario:
  - Si MercadoPago no está configurado o falla, se simula aprobación automática y se guarda en `payments.Payment`
  - La orden permanece en estado `pendiente` hasta confirmación manual del vendedor

## Estructura de datos (resumen)

- `accounts.User`: rol, cédula, teléfono, ubicación, `can_sell`
- `accounts.Farm`: finca simple unida a usuario
- `core.Farm`: finca técnica detallada (suelo, riego, coordenadas, áreas)
- `inventory.Crop`: cultivo asociado a `core.Farm`
- `marketplace.Publication`: oferta de venta basada en `Crop`
- `cart.Cart` / `cart.CartItem`
- `sales.Conversation` / `Message` (chat simple por publicación)
- `sales.Order`: pedido con estados
- `sales.Rating`: calificaciones comprador↔vendedor
- `core.Notification`: notificaciones por usuario
- `payments.Payment`: pago vinculado 1:1 a `Order`

## Endpoints principales

- Página principal: `/`
- Marketplace: `/marketplace/`
- Publicaciones: `/publication/...`
- Carrito: `/cart/`
- Pedidos: `/order/...`
- Conversaciones: `/conversations/` y `/api/conversations/`
- Notificaciones: `/core/...`
- Pagos: `/payments/...`

## Despliegue (Coolify/Docker)

- Imagen basada en `python:3.11-slim`
- Instala `requirements.txt`
- Ejecuta `collectstatic` en build
- Produce con Gunicorn: `CMD ["gunicorn", "--bind", "0.0.0.0:8000", "agroconnect.wsgi:application"]`

Variables mínimas en producción:
- `DEBUG=False`
- `SECRET_KEY`
- `ALLOWED_HOSTS`
- `DATABASE_URL` (PostgreSQL)
- `MERCADOPAGO_ACCESS_TOKEN`
- (Opcional) Cloudinary y Gemini si se usan

## Estructura del proyecto (resumen)

```
AgroConnect/
├── accounts/         # Usuarios, perfiles, fincas simples
├── core/             # BaseModel, Notification, Farm (técnica), vistas core
├── inventory/        # Crop (cultivos)
├── marketplace/      # Publication (publicaciones)
├── cart/             # Cart, CartItem
├── sales/            # Order, Conversation, Message, Rating
├── payments/         # Payment + integración MercadoPago
├── templates/        # HTML
├── static/           # CSS/JS/imagenes (sirve WhiteNoise en prod)
├── agroconnect/      # settings/urls/wsgi
├── Dockerfile
├── requirements.txt
└── manage.py
```

## IA (opcional)

- Asistente: `core.views.assistant_reply`
- Sugerencias IA: `core.views.ai_publication_suggestions`
- Requiere `GOOGLE_API_KEY`/`GEMINI_API_KEY` si se desea usar

## Notas y pendientes

- Chat en tiempo real por WebSockets está deshabilitado; actualmente se usa polling simple (Channels comentado en `requirements.txt` y `settings.py`).
- Existen referencias históricas a ePayco en migraciones y una vista de simulación que no se usa en el flujo actual. No afectan el funcionamiento, pero se recomienda limpiar esos restos en una próxima iteración.
- En modo demo/sandbox, el sistema puede simular pagos aprobados para fines académicos.

## Licencia

MIT
