from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Elimina todas las tablas y recrea la base de datos desde cero'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('🗑️  Eliminando todas las tablas...'))
        
        with connection.cursor() as cursor:
            # Obtener todas las tablas
            cursor.execute("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public';
            """)
            tables = cursor.fetchall()
            
            # Eliminar cada tabla
            for table in tables:
                table_name = table[0]
                self.stdout.write(f'Eliminando tabla: {table_name}')
                cursor.execute(f'DROP TABLE IF EXISTS "{table_name}" CASCADE;')
            
            # Eliminar la tabla de migraciones de Django
            cursor.execute('DROP TABLE IF EXISTS django_migrations CASCADE;')
        
        self.stdout.write(self.style.SUCCESS('✅ Todas las tablas eliminadas correctamente'))
        self.stdout.write(self.style.WARNING('🔄 Ahora ejecuta: python manage.py migrate'))

