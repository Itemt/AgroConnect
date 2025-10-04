#!/usr/bin/env python
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
django.setup()

from django.db import connection
from inventory.models import Crop
from marketplace.models import Publication

def check_database_structure():
    """Verificar la estructura de la base de datos"""
    print("=== Verificando estructura de la base de datos ===")
    
    with connection.cursor() as cursor:
        # Verificar si la tabla inventory_crop existe
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'inventory_crop'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\nColumnas en inventory_crop:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")
        
        # Verificar si la tabla marketplace_publication existe
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'marketplace_publication'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        print(f"\nColumnas en marketplace_publication:")
        for col_name, col_type in columns:
            print(f"  - {col_name}: {col_type}")

def test_queries():
    """Probar las consultas que están fallando"""
    print("\n=== Probando consultas ===")
    
    try:
        # Probar consulta simple de Crop
        crops = Crop.objects.all()[:5]
        print(f"Crops encontrados: {crops.count()}")
        for crop in crops:
            print(f"  - {crop.nombre} ({crop.categoria})")
    except Exception as e:
        print(f"Error en consulta de Crop: {e}")
    
    try:
        # Probar consulta de Publication con select_related
        publications = Publication.objects.filter(
            estado='Activa', 
            cantidad_disponible__gt=0
        ).select_related(
            'cultivo__productor__producer_profile'
        )[:5]
        print(f"Publications encontradas: {publications.count()}")
        for pub in publications:
            print(f"  - {pub.cultivo.nombre} por {pub.cultivo.productor.username}")
    except Exception as e:
        print(f"Error en consulta de Publication: {e}")

if __name__ == "__main__":
    check_database_structure()
    test_queries()