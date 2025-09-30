# AgroConnect

AgroConnect es una plataforma web desarrollada con Django que conecta directamente a productores agrícolas con compradores, eliminando intermediarios y facilitando un comercio más justo y eficiente.

## 🚀 Características Principales

### 👥 Sistema de Usuarios
- **Roles diferenciados:** Productores y Compradores con funcionalidades específicas.
- **Autenticación segura:** Sistema de registro e inicio de sesión.
- **Perfiles detallados:** Información completa de cada usuario.

### 🌾 Gestión de Inventario (Productores)
- **Gestión de cultivos:** Registro de productos, cantidades y fechas de cosecha.
- **Estados de cultivo:** Seguimiento desde siembra hasta cosecha.
- **Dashboard completo:** Panel de control con estadísticas y métricas.
- **Publicación automática:** Conversión de cultivos listos en publicaciones del marketplace.

### 🛒 Marketplace y Carrito de Compras
- **Catálogo de productos:** Visualización de todos los productos disponibles.
- **Búsqueda y filtros:** Encontrar productos específicos fácilmente.
- **Carrito de compras:** Añadir productos, modificar cantidades y eliminar artículos.
- **Resumen de compra:** Cálculo automático del total del pedido.
- **Pago por WhatsApp:** Generación de un mensaje de WhatsApp con los detalles del pedido para finalizar la compra.

### 📦 Sistema de Pedidos Avanzado
- **Flujo completo:** Desde pedido hasta entrega y calificación.
- **Estados detallados:** Pendiente → Confirmado → En Preparación → Enviado → En Tránsito → Entregado → Completado.
- **Gestión por roles:**
  - **Compradores:** Realizar pedidos, confirmar recepción, calificar vendedores.
  - **Productores:** Confirmar pedidos, actualizar estados, gestionar entregas.
- **Cancelación inteligente:** Posibilidad de cancelar con devolución de stock.
- **Historial completo:** Seguimiento detallado de todos los todos los pedidos.

### ⭐ Sistema de Calificaciones y Rankings
- **Calificaciones detalladas:** Puntuación en múltiples aspectos (general, comunicación, puntualidad, calidad).
- **Rankings públicos:** Lista de mejores productores y compradores.
- **Comentarios y recomendaciones:** Feedback detallado entre usuarios.
- **Estadísticas automáticas:** Cálculo automático de promedios y métricas.

### 💬 Sistema de Mensajería
- **Comunicación directa:** Chat entre compradores y productores.
- **Conversaciones por producto:** Organización por publicación.
- **Historial de mensajes:** Registro completo de comunicaciones.
- **Notificaciones:** Alertas de nuevos mensajes.

### 📊 Analytics y Estadísticas
- **Dashboard del Productor:**
  - Ingresos totales y pendientes.
  - Estadísticas de ventas por producto.
  - Top compradores y análisis de tendencias.
  - Pedidos que requieren atención.
  - Calificaciones recientes.
- **Dashboard del Comprador:**
  - Historial de compras.
  - Gastos totales.
  - Productos favoritos.
  - Calificaciones dadas.

## 🛠 Tecnologías Utilizadas

- **Backend:** Python 3.9+, Django 4.2
- **Frontend:** HTML5, CSS3 (TailwindCSS), JavaScript
- **Base de Datos:** SQLite (desarrollo), PostgreSQL (producción)
- **Librerías Python:**
  - `django-crispy-forms`
  - `Pillow`
  - `Faker`

## 📋 Instalación y Puesta en Marcha

### 1. Clonar el Repositorio

```bash
git clone https://github.com/tu_usuario/agroconnect.git
cd agroconnect
```

### 2. Crear y Activar Entorno Virtual

```bash
# Crear el entorno virtual
python -m venv venv

# Activar en macOS/Linux
source venv/bin/activate

# Activar en Windows
venv\\Scripts\\activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Base de Datos

```bash
# Aplicar migraciones
python manage.py migrate

# Crear superusuario (opcional)
python manage.py createsuperuser
```

### 5. Generar Datos de Prueba (Recomendado)

```bash
# Poblar con datos de ejemplo
python manage.py seed_data
```

### 6. Ejecutar el Servidor

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/`.

## 🔄 Flujo de Trabajo Típico

### Para un Productor:
1.  **Registrar cultivos** con información detallada.
2.  **Publicar productos** cuando estén listos para venta.
3.  **Recibir y confirmar pedidos** de compradores.
4.  **Actualizar estados** de pedidos (preparación, envío, entrega).
5.  **Recibir calificaciones** y mejorar el servicio.

### Para un Comprador:
1.  **Explorar el marketplace** y buscar productos.
2.  **Añadir productos** al carrito de compras.
3.  **Revisar el carrito** y ajustar las cantidades.
4.  **Proceder al pago** a través de WhatsApp.
5.  **Contactar productores** para negociar detalles (si es necesario).
6.  **Seguir el estado** del pedido hasta la entrega.
7.  **Confirmar recepción** y calificar al productor.

## 🚀 Próximas Funcionalidades

- [ ] Sistema de pagos integrado (Stripe, MercadoPago).
- [ ] Notificaciones push y por email.
- [ ] API REST para aplicaciones móviles.
- [ ] Sistema de logística y tracking GPS.

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor, abre un *issue* para discutir los cambios que te gustaría hacer.