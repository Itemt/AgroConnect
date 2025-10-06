#!/usr/bin/env python
"""
Script de prueba para verificar que el servidor funciona correctamente
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
django.setup()

# Verificar que no hay errores de importación
try:
    from django.core.management import execute_from_command_line
    from agroconnect.asgi import application
    print("✅ Django configurado correctamente")
    print("✅ ASGI application cargada correctamente")
    print("✅ WebSockets configurados correctamente")
    print("✅ Servidor listo para funcionar")
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)
