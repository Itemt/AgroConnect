#!/usr/bin/env python
"""
Script para migrar datos de SQLite a PostgreSQL
"""
import os
import sys
import django
from django.conf import settings
from django.core.management import execute_from_command_line

def migrate_to_postgres():
    """Migrar datos de SQLite a PostgreSQL"""
    
    print("🔄 Iniciando migración de SQLite a PostgreSQL...")
    
    # Paso 1: Crear nuevas migraciones
    print("📝 Creando migraciones para PostgreSQL...")
    execute_from_command_line(['manage.py', 'makemigrations'])
    
    # Paso 2: Aplicar migraciones en PostgreSQL
    print("🗄️ Aplicando migraciones en PostgreSQL...")
    execute_from_command_line(['manage.py', 'migrate'])
    
    # Paso 3: Cargar datos del backup
    print("📥 Cargando datos desde backup...")
    try:
        execute_from_command_line(['manage.py', 'loaddata', 'data_backup.json'])
        print("✅ Migración completada exitosamente!")
    except Exception as e:
        print(f"⚠️ Error cargando datos: {e}")
        print("💡 Puedes cargar los datos manualmente después del deployment")

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
    django.setup()
    migrate_to_postgres()
