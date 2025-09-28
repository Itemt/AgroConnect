# AgroConnect

AgroConnect es una plataforma web desarrollada con Django que conecta directamente a productores agrícolas con compradores, eliminando intermediarios y facilitando un comercio más justo y eficiente.

## 🚀 Características Principales

### 👥 Sistema de Usuarios
- **Roles diferenciados:** Productores y Compradores con funcionalidades específicas
- **Autenticación segura:** Sistema de registro e inicio de sesión
- **Perfiles detallados:** Información completa de cada usuario

### 🌾 Gestión de Inventario (Productores)
- **Gestión de cultivos:** Registro de productos, cantidades y fechas de cosecha
- **Estados de cultivo:** Seguimiento desde siembra hasta cosecha
- **Dashboard completo:** Panel de control con estadísticas y métricas
- **Publicación automática:** Conversión de cultivos listos en publicaciones del marketplace

### 🛒 Marketplace Integrado
- **Catálogo de productos:** Visualización de todos los productos disponibles
- **Búsqueda y filtros:** Encontrar productos específicos fácilmente
- **Información detallada:** Precios, cantidades, ubicación y datos del productor
- **Publicaciones dinámicas:** Actualización automática de disponibilidad

### 📦 Sistema de Pedidos Avanzado
- **Flujo completo:** Desde pedido hasta entrega y calificación
- **Estados detallados:** Pendiente → Confirmado → En Preparación → Enviado → En Tránsito → Entregado → Completado
- **Gestión por roles:**
  - **Compradores:** Realizar pedidos, confirmar recepción, calificar vendedores
  - **Productores:** Confirmar pedidos, actualizar estados, gestionar entregas
- **Cancelación inteligente:** Posibilidad de cancelar con devolución de stock
- **Historial completo:** Seguimiento detallado de todos los pedidos

### ⭐ Sistema de Calificaciones y Rankings
- **Calificaciones detalladas:** Puntuación en múltiples aspectos (general, comunicación, puntualidad, calidad)
- **Rankings públicos:** Lista de mejores productores y compradores
- **Comentarios y recomendaciones:** Feedback detallado entre usuarios
- **Estadísticas automáticas:** Cálculo automático de promedios y métricas

### 💬 Sistema de Mensajería
- **Comunicación directa:** Chat entre compradores y productores
- **Conversaciones por producto:** Organización por publicación
- **Historial de mensajes:** Registro completo de comunicaciones
- **Notificaciones:** Alertas de nuevos mensajes

### 📊 Analytics y Estadísticas
- **Dashboard del Productor:**
  - Ingresos totales y pendientes
  - Estadísticas de ventas por producto
  - Top compradores y análisis de tendencias
  - Pedidos que requieren atención
  - Calificaciones recientes
- **Dashboard del Comprador:**
  - Historial de compras
  - Gastos totales
  - Productos favoritos
  - Calificaciones dadas

### 🔍 Búsqueda y Filtros Avanzados
- **Filtros múltiples:** Por estado, fecha, producto, usuario
- **Búsqueda inteligente:** En nombres de productos y usuarios
- **Paginación:** Navegación eficiente en listas grandes
- **Ordenamiento:** Por relevancia, fecha, precio

## 🛠 Tecnologías Utilizadas

- **Backend:** Python 3.9+, Django 4.2
- **Frontend:** HTML5, CSS3, JavaScript
- **Base de Datos:** SQLite (desarrollo), PostgreSQL (producción)
- **Librerías Python:** 
  - Faker (generación de datos de prueba)
  - Django ORM (gestión de base de datos)
  - Django Forms (validación de formularios)

## 📋 Instalación y Puesta en Marcha

### 1. Clonar el Repositorio

```bash
git clone <URL-del-repositorio>
cd agroconnect
```

### 2. Crear y Activar Entorno Virtual

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar en macOS/Linux
source venv/bin/activate

# Activar en Windows
venv\Scripts\activate
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

Este comando crea:
- Usuarios de prueba (productores y compradores)
- Cultivos y productos variados
- Publicaciones en el marketplace
- Pedidos de ejemplo
- Conversaciones y mensajes
- Calificaciones de muestra

### 6. Ejecutar el Servidor

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/`

## 🎯 Usuarios de Prueba

Después de ejecutar `seed_data`, puedes usar estas cuentas:

### Productores:
- **Usuario:** `juan.gonzalez` | **Contraseña:** `password123`
- **Usuario:** `maria.rodriguez` | **Contraseña:** `password123`

### Compradores:
- **Usuario:** `carlos.martinez` | **Contraseña:** `password123`
- **Usuario:** `ana.lopez` | **Contraseña:** `password123`

### Administrador:
- **Usuario:** `admin` | **Contraseña:** `admin`

## 🗺 Navegación de la Aplicación

### Para Productores:
1. **Dashboard:** `/producer/dashboard/` - Vista general de cultivos y ventas
2. **Mis Cultivos:** `/producer/crops/` - Gestión de cultivos
3. **Panel de Ventas:** `/producer/sales/` - Análisis detallado de ventas
4. **Historial de Pedidos:** `/order/history/` - Todos los pedidos recibidos

### Para Compradores:
1. **Marketplace:** `/marketplace/` - Catálogo de productos
2. **Mi Dashboard:** `/buyer/dashboard/` - Vista general de compras
3. **Historial de Pedidos:** `/order/history/` - Todos los pedidos realizados
4. **Mis Mensajes:** `/conversations/` - Comunicaciones con productores

### Para Todos:
1. **Rankings:** `/rankings/` - Mejores usuarios de la plataforma
2. **Mi Perfil:** `/accounts/profile/` - Información personal
3. **Conversaciones:** `/conversations/` - Sistema de mensajería

## 🔄 Flujo de Trabajo Típico

### Para un Productor:
1. **Registrar cultivos** con información detallada
2. **Publicar productos** cuando estén listos para venta
3. **Recibir y confirmar pedidos** de compradores
4. **Actualizar estados** de pedidos (preparación, envío, entrega)
5. **Recibir calificaciones** y mejorar el servicio

### Para un Comprador:
1. **Explorar el marketplace** y buscar productos
2. **Contactar productores** para negociar detalles
3. **Realizar pedidos** con cantidades específicas
4. **Seguir el estado** del pedido hasta la entrega
5. **Confirmar recepción** y calificar al productor

## 📊 Funcionalidades Avanzadas

### Sistema de Estados de Pedidos:
- **Pendiente:** Pedido creado, esperando confirmación
- **Confirmado:** Productor acepta el pedido
- **En Preparación:** Producto siendo preparado
- **Enviado:** Pedido despachado
- **En Tránsito:** Pedido en camino
- **Entregado:** Pedido llegó al destino
- **Completado:** Comprador confirma recepción
- **Cancelado:** Pedido cancelado por cualquier parte

### Sistema de Calificaciones:
- **Puntuación General:** Satisfacción global (1-5 estrellas)
- **Comunicación:** Calidad de la comunicación
- **Puntualidad:** Cumplimiento de tiempos
- **Calidad del Producto:** Estado y calidad del producto
- **Comentarios:** Feedback detallado
- **Recomendación:** ¿Recomendaría a otros usuarios?

### Analytics Automáticos:
- **Métricas de Ventas:** Ingresos, volúmenes, tendencias
- **Análisis de Productos:** Productos más vendidos
- **Comportamiento de Usuarios:** Patrones de compra
- **Tasas de Conversión:** Eficiencia de ventas
- **Satisfacción del Cliente:** Promedios de calificaciones

## 🔧 Panel de Administración

Accede en `http://127.0.0.1:8000/admin/` para:
- Gestionar usuarios y perfiles
- Supervisar pedidos y transacciones
- Moderar calificaciones y comentarios
- Ver estadísticas globales de la plataforma
- Configurar parámetros del sistema

## 🚀 Próximas Funcionalidades

- [ ] Sistema de pagos integrado
- [ ] Notificaciones push y por email
- [ ] API REST para aplicaciones móviles
- [ ] Sistema de logística y tracking GPS
- [ ] Marketplace de servicios agrícolas
- [ ] Integración con sistemas de inventario externos
- [ ] Análisis predictivo de demanda
- [ ] Sistema de contratos inteligentes

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu funcionalidad (`git checkout -b feature/nueva-funcionalidad`)
3. Commit tus cambios (`git commit -am 'Añadir nueva funcionalidad'`)
4. Push a la rama (`git push origin feature/nueva-funcionalidad`)
5. Crea un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo `LICENSE` para más detalles.

## 📞 Soporte

Para soporte técnico o consultas sobre el proyecto:
- Crear un issue en GitHub
- Contactar al equipo de desarrollo

---

**AgroConnect** - Conectando el campo con la mesa 🌾🍽️