#!/bin/bash

echo "🚀 Iniciando AgroConnect con PostgreSQL..."

# Esperar un poco para que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
sleep 5

# Crear migraciones frescas
echo "📝 Creando migraciones..."
python manage.py makemigrations

# Aplicar migraciones
echo "🗄️ Aplicando migraciones..."
python manage.py migrate

# Iniciar Gunicorn
echo "🌟 Iniciando servidor..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 agroconnect.wsgi:application
