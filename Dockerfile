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
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copiar el código de la aplicación
COPY . .

# Crear directorio para archivos estáticos
RUN mkdir -p staticfiles

# Recopilar archivos estáticos
RUN python manage.py collectstatic --noinput

# Nota: Las migraciones se ejecutarán en runtime para PostgreSQL

# Exponer el puerto
EXPOSE 8000

# Copiar y configurar script de inicio
COPY start.sh .
RUN sed -i 's/\r$//' start.sh && chmod +x start.sh

# Comando para ejecutar la aplicación con inicialización de PostgreSQL
CMD ["./start.sh"]
