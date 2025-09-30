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

### 🌾 Gestión de Inventario (Productores)
- **Gestión de cultivos completa:**
  - Registro de productos con nombre personalizado
  - 6 categorías principales: Hortalizas, Frutas, Granos, Tubérculos, Aromáticas, Otros
  - Cantidad estimada y unidades de medida (kg, ton, und, etc.)
  - Ubicación precisa (departamento y ciudad)
  - Imágenes de los cultivos
- **Estados de cultivo:** 
  - Siembra → Crecimiento → Listo para Cosecha → Cosechado
- **Dashboard del productor:**
  - Resumen de cultivos activos
  - Ingresos totales y pendientes
  - Estadísticas de ventas por producto
  - Pedidos recientes y que requieren atención
  - Top compradores y productos más vendidos
- **Publicaciones:** Conversión directa de cultivos en publicaciones del marketplace.

### 🛒 Marketplace y Carrito de Compras
- **Catálogo de productos dinámico:**
  - Grid responsivo de productos con imágenes
  - Badges de categoría y precio
  - Vista detallada de cada publicación
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
  - Editar precio, cantidad, descripción e imagen
  - Eliminar publicaciones sin afectar el cultivo
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

### 📊 Analytics y Estadísticas Detalladas

#### Dashboard del Productor:
- **Métricas financieras:**
  - Ingresos totales generados
  - Ingresos pendientes de cobro
  - Gráficos de tendencias de ventas
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
- **Django Channels** - WebSockets para chat en tiempo real
- **Pillow** - Procesamiento de imágenes

### Frontend
- **HTML5 / CSS3**
- **TailwindCSS** - Framework CSS moderno
- **JavaScript (Vanilla)** - Interactividad del lado del cliente
- **Font Awesome** - Iconografía

### Base de Datos
- **SQLite** - Desarrollo local
- **PostgreSQL** - Producción

### Deployment
- **Docker** - Containerización
- **Coolify** - Plataforma de despliegue
- **Git** - Control de versiones

### Librerías Python Principales
```
Django==4.2.16
channels==4.1.0
pillow==11.0.0
psycopg2-binary==2.9.10
faker==33.1.0
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
Para desarrollo local, Django usará SQLite por defecto. Para PostgreSQL, configura:
```bash
# Crear archivo .env en la raíz del proyecto
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=agroconnect
POSTGRES_USER=tu_usuario
POSTGRES_PASSWORD=tu_contraseña
```

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

### Opción 2: Docker (Producción)

#### 1. Construir la Imagen
```bash
docker build -t agroconnect:latest .
```

#### 2. Ejecutar con Docker Compose (recomendado)
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: agroconnect
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: tu_password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  web:
    image: agroconnect:latest
    environment:
      POSTGRES_HOST: db
      POSTGRES_PORT: 5432
      POSTGRES_DB: agroconnect
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: tu_password
    ports:
      - "8000:8000"
    depends_on:
      - db

volumes:
  postgres_data:
```

#### 3. Iniciar los Servicios
```bash
docker-compose up -d
```

## 🗂️ Estructura del Proyecto

```
AgroConnect/
├── accounts/           # Gestión de usuarios y perfiles
│   ├── models.py      # User, ProducerProfile, BuyerProfile
│   ├── views.py       # Autenticación, registro, perfiles
│   └── forms.py       # Formularios de usuario
├── inventory/         # Gestión de cultivos (productores)
│   ├── models.py      # Crop
│   ├── views.py       # CRUD de cultivos, dashboard
│   └── forms.py       # Formularios de cultivos
├── marketplace/       # Marketplace y publicaciones
│   ├── models.py      # Publication
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
├── core/              # Funcionalidades compartidas
│   └── colombia_locations.py  # Base de datos de ubicaciones
├── templates/         # Plantillas HTML
├── static/            # Archivos estáticos (CSS, JS, imágenes)
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
1. **Registrarse** como productor con información de negocio y ubicación
2. **Crear cultivos** con detalles completos (nombre, categoría, cantidad, ubicación, imagen)
3. **Actualizar estado** de cultivos conforme crecen
4. **Publicar productos** cuando estén listos para venta
5. **Recibir y gestionar pedidos** de compradores
6. **Actualizar estados de envío** (preparación → enviado → entregado)
7. **Recibir calificaciones** y construir reputación
8. **Analizar métricas** de ventas en el dashboard
9. **Comunicarse** con compradores vía chat en tiempo real

### Para un Comprador:
1. **Registrarse** como comprador con información de contacto
2. **Explorar el marketplace** con filtros avanzados
3. **Ver detalles** de productos y perfiles de productores
4. **Añadir productos** al carrito con cantidades deseadas
5. **Contactar productores** para negociar detalles
6. **Realizar pedido** desde el carrito
7. **Seguir el estado** del pedido en tiempo real
8. **Confirmar recepción** cuando el producto llegue
9. **Calificar al productor** y dejar comentarios
10. **Ver historial** de compras y gastos totales

### Para un Administrador:
1. **Gestionar usuarios** (crear, editar, eliminar)
2. **Moderar publicaciones** y contenido
3. **Revisar pedidos** y resolver disputas
4. **Monitorear estadísticas** generales de la plataforma
5. **Gestionar categorías** y configuraciones

## 📱 Características de UX/UI

- ✨ **Diseño moderno** con TailwindCSS
- 📱 **Totalmente responsivo** (móvil, tablet, desktop)
- 🎨 **Interfaz intuitiva** con iconografía clara
- ⚡ **Carga rápida** con optimización de assets
- 🔔 **Notificaciones visuales** para acciones del usuario
- 🌈 **Esquema de colores consistente** (verde agrícola)
- 💬 **Chat en tiempo real** sin necesidad de recargar
- 🔍 **Búsqueda instantánea** con sugerencias
- ✅ **Validación de formularios** en tiempo real
- 🖼️ **Optimización de imágenes** automática

## 🔐 Seguridad

- 🔒 **Autenticación robusta** con Django Auth
- 🛡️ **Protección CSRF** en todos los formularios
- 🚫 **Validación de permisos** por rol
- 🔑 **Contraseñas hasheadas** con algoritmos seguros
- 📝 **Sanitización de inputs** para prevenir XSS
- 🌐 **Protección contra SQL injection** con ORM de Django
- 🔐 **Variables de entorno** para datos sensibles

## 🚀 Próximas Funcionalidades

- [ ] Sistema de pagos integrado (Mercado Pago, PSE)
- [ ] Notificaciones push y por email
- [ ] API REST con Django REST Framework
- [ ] Aplicación móvil nativa (React Native)
- [ ] Sistema de logística y tracking GPS
- [ ] Certificaciones de productos orgánicos
- [ ] Marketplace de insumos agrícolas
- [ ] Pronósticos de precios con ML
- [ ] Sistema de subastas inversas
- [ ] Integración con APIs climáticas

## 📊 Modelos de Datos Principales

### User (Django AbstractUser)
- Roles: productor, comprador, administrador
- Información de contacto y perfil

### Crop (Cultivo)
- Nombre, categoría, cantidad, unidad
- Estado: siembra → crecimiento → listo → cosechado
- Ubicación y fecha de disponibilidad
- Relación con productor

### Publication (Publicación)
- Relación con cultivo
- Precio, cantidad disponible, cantidad mínima
- Estado: Activa, Vendida, Inactiva
- Imagen y descripción

### Order (Pedido)
- Relación con publicación, comprador, vendedor
- Cantidad, precio total
- Estado: 7 estados diferentes
- Timestamps de cada cambio de estado

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
