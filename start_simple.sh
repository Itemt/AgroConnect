#!/bin/bash

echo "🚀 Iniciando AgroConnect (versión simple)..."

# Esperar un momento para que los servicios estén listos
echo "⏳ Esperando inicialización de servicios..."
sleep 5

# Aplicar migraciones
echo "🗄️ Aplicando migraciones..."
python manage.py migrate --noinput

# Recopilar archivos estáticos
echo "📦 Recopilando archivos estáticos..."
python manage.py collectstatic --noinput

# Iniciar con Gunicorn (más simple, sin WebSockets)
echo "🌟 Iniciando servidor con Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 agroconnect.wsgi:application
