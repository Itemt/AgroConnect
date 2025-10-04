#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
django.setup()

from django.db import connection, transaction

def fix_database():
    """Corregir la estructura de la base de datos"""
    print("=== Corrigiendo estructura de la base de datos ===")
    
    with connection.cursor() as cursor:
        with transaction.atomic():
            # Verificar si la columna nombre existe
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'inventory_crop' AND column_name = 'nombre';
            """)
            
            if not cursor.fetchone():
                print("Agregando columna 'nombre' a inventory_crop...")
                cursor.execute("""
                    ALTER TABLE inventory_crop 
                    ADD COLUMN nombre VARCHAR(100) DEFAULT 'Cultivo sin nombre';
                """)
                
                # Actualizar los registros existentes con nombres genéricos
                cursor.execute("""
                    UPDATE inventory_crop 
                    SET nombre = 'Cultivo ' || id::text 
                    WHERE nombre = 'Cultivo sin nombre';
                """)
            
            # Verificar si la columna categoria existe
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'inventory_crop' AND column_name = 'categoria';
            """)
            
            if not cursor.fetchone():
                print("Agregando columna 'categoria' a inventory_crop...")
                cursor.execute("""
                    ALTER TABLE inventory_crop 
                    ADD COLUMN categoria VARCHAR(30) DEFAULT 'otros';
                """)
            
            # Verificar si la columna producto_id existe y eliminarla si es necesario
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'inventory_crop' AND column_name = 'producto_id';
            """)
            
            if cursor.fetchone():
                print("Eliminando columna 'producto_id' de inventory_crop...")
                cursor.execute("""
                    ALTER TABLE inventory_crop 
                    DROP COLUMN producto_id;
                """)
            
            print("Estructura de la base de datos corregida exitosamente!")

if __name__ == "__main__":
    fix_database()
