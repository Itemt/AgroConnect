# AgroConnect

AgroConnect es una plataforma web desarrollada con Django que tiene como objetivo conectar directamente a productores agrícolas con compradores, eliminando intermediarios y facilitando un comercio más justo y eficiente.

## Características Principales

- **Roles de Usuario:** Sistema de autenticación con dos tipos de perfiles: **Productor** y **Comprador**.
- **Gestión de Inventario:** Los productores pueden gestionar sus cultivos, especificando productos, cantidades y fechas estimadas de cosecha.
- **Marketplace Integrado:** Un mercado donde los productores publican sus productos disponibles para la venta.
- **Sistema de Mensajería Interna:** Comunicación directa entre compradores y productores para negociar precios y logística.
- **Gestión de Perfiles:** Los usuarios pueden ver y actualizar su información personal y de perfil.
- **Población de Datos de Prueba:** Incluye un comando para generar datos ficticios (usuarios, productos, publicaciones), ideal para demostraciones y desarrollo.

## Tecnologías Utilizadas

- **Backend:** Python, Django
- **Frontend:** HTML5, CSS3
- **Base de Datos:** SQLite (para desarrollo)
- **Librerías Python:** Faker (para la generación de datos de prueba)

## Instalación y Puesta en Marcha

Sigue estos pasos para configurar y ejecutar el proyecto en tu entorno local.

### 1. Clonar el Repositorio

```bash
git clone <URL-del-repositorio-en-GitHub>
cd agroconnect
```

### 2. Crear y Activar un Entorno Virtual

Es altamente recomendable usar un entorno virtual para aislar las dependencias del proyecto.

```bash
# Crear el entorno virtual
python3 -m venv venv

# Activar en macOS/Linux
source venv/bin/activate

# Activar en Windows
# venv\\Scripts\\activate
```

### 3. Instalar Dependencias

Instala todas las librerías necesarias que se encuentran en el archivo `requirements.txt`.

```bash
pip install -r requirements.txt
```
*(Nota: Necesitaremos crear el archivo `requirements.txt` a continuación)*

### 4. Aplicar Migraciones

Crea las tablas en la base de datos ejecutando las migraciones de Django.

```bash
python manage.py migrate
```

### 5. Generar Datos de Prueba (Opcional pero recomendado)

Para tener una experiencia completa desde el inicio, puedes poblar la base de datos con usuarios (productores y compradores), productos y publicaciones de prueba.

```bash
python manage.py seed_data
```

### 6. Crear un Superusuario

Para acceder al panel de administración de Django, necesitas una cuenta de administrador.

```bash
python manage.py createsuperuser
```
*(También puedes usar el superusuario `admin` con contraseña `admin` si ejecutas `seed_data` después de las migraciones)*

### 7. Ejecutar el Servidor de Desarrollo

¡Listo! Inicia el servidor.

```bash
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/`.

## Acceso al Panel de Administración

Puedes acceder al panel de administración en `http://127.0.0.1:8000/admin/`.

- **Usuario:** `admin`
- **Contraseña:** `admin`
*(Estas credenciales son creadas por el comando `seed_data`)*.
