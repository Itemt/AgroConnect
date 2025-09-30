#!/bin/bash

echo "🚀 Iniciando AgroConnect con PostgreSQL..."

# Verificar que las variables de entorno de la base de datos están configuradas
if [ -z "$POSTGRES_HOST" ] || [ -z "$POSTGRES_PORT" ] || [ -z "$POSTGRES_USER" ]; then
  echo "❌ Error: Las variables de entorno de la base de datos (POSTGRES_HOST, POSTGRES_PORT, POSTGRES_USER) no están configuradas."
  echo "Por favor, configura estas variables en tu entorno de producción y vuelve a desplegar."
  exit 1
fi

# Esperar a que PostgreSQL esté listo
echo "⏳ Esperando a que PostgreSQL esté listo en $POSTGRES_HOST:$POSTGRES_PORT..."
export PGPASSWORD=$POSTGRES_PASSWORD # pg_isready necesita la contraseña

until pg_isready -h "$POSTGRES_HOST" -p "$POSTGRES_PORT" -U "$POSTGRES_USER" -d "$POSTGRES_DB"; do
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
