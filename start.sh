#!/bin/bash

echo "🚀 Iniciando AgroConnect..."

# Esperar un momento para que los servicios estén listos
echo "⏳ Esperando inicialización de servicios..."
sleep 10

# Aplicar migraciones
echo "🗄️ Aplicando migraciones..."
python manage.py migrate --noinput

# Iniciar Gunicorn
echo "🌟 Iniciando servidor..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 agroconnect.wsgi:application
