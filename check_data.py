#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
django.setup()

from django.db import connection

def check_data():
    """Verificar qué datos hay en las tablas"""
    print("=== Verificando datos existentes ===")
    
    with connection.cursor() as cursor:
        # Verificar datos en inventory_crop
        cursor.execute("SELECT COUNT(*) FROM inventory_crop;")
        crop_count = cursor.fetchone()[0]
        print(f"Registros en inventory_crop: {crop_count}")
        
        if crop_count > 0:
            cursor.execute("SELECT * FROM inventory_crop LIMIT 3;")
            rows = cursor.fetchall()
            print("Primeros 3 registros:")
            for row in rows:
                print(f"  {row}")
        
        # Verificar datos en marketplace_publication
        cursor.execute("SELECT COUNT(*) FROM marketplace_publication;")
        pub_count = cursor.fetchone()[0]
        print(f"\nRegistros en marketplace_publication: {pub_count}")
        
        if pub_count > 0:
            cursor.execute("SELECT * FROM marketplace_publication LIMIT 3;")
            rows = cursor.fetchall()
            print("Primeros 3 registros:")
            for row in rows:
                print(f"  {row}")

if __name__ == "__main__":
    check_data()
