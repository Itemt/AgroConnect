# Templates de Error - AgroConnect

Esta carpeta contiene los templates personalizados para manejar errores HTTP en AgroConnect.

## 📁 Archivos incluidos

### 403.html - Acceso Denegado
- **Código de error**: 403 Forbidden
- **Cuándo se muestra**: Cuando el usuario no tiene permisos para acceder a una página
- **Diseño**: Colores naranjas/amarillos con icono de candado
- **Características**:
  - Explicación clara del error
  - Información sobre la cuenta del usuario (si está autenticado)
  - Botones para ir al inicio o perfil
  - Animaciones con iconos de seguridad

### 404.html - Página No Encontrada
- **Código de error**: 404 Not Found
- **Cuándo se muestra**: Cuando se accede a una URL que no existe
- **Diseño**: Colores rojos con icono de advertencia
- **Características**:
  - Enlaces útiles organizados por categorías
  - Búsqueda integrada para encontrar productos
  - Enlaces contextuales según el rol del usuario
  - Animaciones con emojis de productos agrícolas

### 500.html - Error del Servidor
- **Código de error**: 500 Internal Server Error
- **Cuándo se muestra**: Cuando ocurre un error interno del servidor
- **Diseño**: Colores rojos/naranjas con icono de error
- **Características**:
  - Instrucciones claras sobre qué hacer
  - Información de contacto para reportar problemas
  - Botón para recargar la página
  - Animaciones con herramientas de reparación

## 🎨 Diseño

Todos los templates mantienen la identidad visual de AgroConnect:
- **Colores**: Paleta de verdes, rojos, naranjas según el tipo de error
- **Tipografía**: Figtree (consistente con el resto de la aplicación)
- **Componentes**: Botones, tarjetas y animaciones coherentes
- **Responsive**: Adaptado para móviles y desktop

## ⚙️ Configuración

Los handlers están configurados en:
- `agroconnect/settings.py`: Definición de los handlers
- `core/views.py`: Implementación de las vistas de error

## 🔧 Personalización

Para modificar los templates:
1. Edita el archivo correspondiente en esta carpeta
2. Mantén la estructura HTML y clases CSS
3. Actualiza los colores y mensajes según sea necesario
4. Prueba en diferentes dispositivos

## 📱 Responsive Design

Todos los templates están optimizados para:
- **Móviles**: Diseño vertical con botones de ancho completo
- **Tablets**: Layout híbrido con elementos organizados
- **Desktop**: Diseño horizontal con mejor aprovechamiento del espacio

## 🎯 Objetivos

- **Experiencia de usuario**: Páginas de error útiles y atractivas
- **Navegación**: Enlaces claros para continuar usando la plataforma
- **Consistencia**: Mantener la identidad visual de AgroConnect
- **Funcionalidad**: Ayudar al usuario a resolver el problema
