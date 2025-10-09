FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements y instalar dependencias de Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código de la aplicación
COPY . .

# Crear directorios para archivos estáticos y media
RUN mkdir -p staticfiles media

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Nota: Las migraciones se ejecutarán en runtime para PostgreSQL

# Exponer el puerto
EXPOSE 8000

# Comando para ejecutar la aplicación con Gunicorn (más simple)
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "agroconnect.wsgi:application"]
