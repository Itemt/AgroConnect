#!/bin/bash

echo "🚀 Iniciando AgroConnect con PostgreSQL..."

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo..."
# Asumiendo que las variables de entorno para la BD están disponibles
# DB_HOST, DB_PORT, DB_USER, PGPASSWORD
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER; do
  echo "PostgreSQL no está listo todavía. Esperando..."
  sleep 2
done
echo "✅ PostgreSQL está listo."

# Aplicar migraciones
echo "🗄️ Aplicando migraciones..."
python manage.py migrate

# Iniciar Gunicorn
echo "🌟 Iniciando servidor..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 agroconnect.wsgi:application
