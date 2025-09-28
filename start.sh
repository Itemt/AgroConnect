#!/bin/bash

echo "🚀 Iniciando AgroConnect con PostgreSQL..."

# Esperar a que PostgreSQL esté disponible
echo "⏳ Esperando conexión a PostgreSQL..."
python -c "
import os
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_db():
    db_conn = None
    while not db_conn:
        try:
            db_conn = psycopg2.connect(
                host=os.environ.get('POSTGRES_HOST', 'agroconnect'),
                port=os.environ.get('POSTGRES_PORT', '5432'),
                database=os.environ.get('POSTGRES_DB', 'postgres'),
                user=os.environ.get('POSTGRES_USER', 'agroconnect_user'),
                password=os.environ.get('POSTGRES_PASSWORD', '')
            )
            print('✅ PostgreSQL conectado!')
        except OperationalError:
            print('⏳ PostgreSQL no disponible, reintentando...')
            time.sleep(1)

wait_for_db()
" 2>/dev/null || echo "⚠️ Continuando sin verificación de PostgreSQL..."

# Crear migraciones frescas
echo "📝 Creando migraciones..."
python manage.py makemigrations

# Aplicar migraciones
echo "🗄️ Aplicando migraciones..."
python manage.py migrate

# Iniciar Gunicorn
echo "🌟 Iniciando servidor..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 agroconnect.wsgi:application
