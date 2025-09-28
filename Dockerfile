FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar el código de la aplicación
COPY . .

# Crear directorio para archivos estáticos
RUN mkdir -p staticfiles

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Ejecutar migraciones
RUN python manage.py migrate

# Copiar script de migración
COPY migrate_to_postgres.py .
COPY data_backup.json .

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación con Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "agroconnect.wsgi:application"]
