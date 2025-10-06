#!/usr/bin/env python
"""
Script para iniciar el servidor con Daphne (soporte para WebSockets)
"""
import os
import sys
import django
from django.core.management import execute_from_command_line

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'agroconnect.settings')
    django.setup()
    
    # Usar Daphne en lugar de runserver para soporte de WebSockets
    os.system("daphne -b 0.0.0.0 -p 8000 agroconnect.asgi:application")
