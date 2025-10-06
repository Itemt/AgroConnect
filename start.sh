#!/bin/bash

echo "🚀 Iniciando AgroConnect..."

# Esperar un momento para que los servicios estén listos
echo "⏳ Esperando inicialización de servicios..."
sleep 10

# Aplicar migraciones
echo "🗄️ Aplicando migraciones..."
python manage.py migrate --noinput

# Iniciar Daphne (soporte para WebSockets)
echo "🌟 Iniciando servidor con soporte para WebSockets..."
exec daphne -b 0.0.0.0 -p 8000 agroconnect.asgi:application
