# -*- coding: utf-8 -*-
"""
Comando para corregir caracteres mal codificados en la base de datos
"""
from django.core.management.base import BaseCommand
from core.models import Farm


class Command(BaseCommand):
    help = 'Corrige los caracteres mal codificados en departamentos y ciudades'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('Iniciando corrección de caracteres...'))
        
        farms = Farm.objects.all()
        fixed_count = 0
        
        for farm in farms:
            updated = False
            
            # Corregir departamento
            if farm.departamento:
                try:
                    original_departamento = farm.departamento
                    fixed_departamento = original_departamento
                    
                    # Solo intentar arreglar si hay caracteres mal codificados típicos
                    if any(char in fixed_departamento for char in ['Ã', 'Ã©', 'Ã­', 'Ã³', 'Ãº', 'Ã±']):
                        try:
                            # Convertir a bytes asumiendo latin1 y decodificar como utf-8
                            fixed_departamento = fixed_departamento.encode('latin1').decode('utf-8')
                        except (UnicodeDecodeError, UnicodeEncodeError):
                            # Si falla, no hacer nada
                            pass
                    
                    if fixed_departamento != original_departamento:
                        farm.departamento = fixed_departamento
                        updated = True
                        self.stdout.write(
                            f'  Departamento: "{original_departamento}" -> "{fixed_departamento}"'
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  Error al corregir departamento de farm {farm.id}: {e}')
                    )
            
            # Corregir ciudad
            if farm.ciudad:
                try:
                    original_ciudad = farm.ciudad
                    fixed_ciudad = original_ciudad
                    
                    # Solo intentar arreglar si hay caracteres mal codificados típicos
                    if any(char in fixed_ciudad for char in ['Ã', 'Ã©', 'Ã­', 'Ã³', 'Ãº', 'Ã±']):
                        try:
                            # Convertir a bytes asumiendo latin1 y decodificar como utf-8
                            fixed_ciudad = fixed_ciudad.encode('latin1').decode('utf-8')
                        except (UnicodeDecodeError, UnicodeEncodeError):
                            # Si falla, no hacer nada
                            pass
                    
                    if fixed_ciudad != original_ciudad:
                        farm.ciudad = fixed_ciudad
                        updated = True
                        self.stdout.write(
                            f'  Ciudad: "{original_ciudad}" -> "{fixed_ciudad}"'
                        )
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(f'  Error al corregir ciudad de farm {farm.id}: {e}')
                    )
            
            if updated:
                farm.save()
                fixed_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'OK Finca "{farm.nombre}" actualizada')
                )
        
        if fixed_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'\nOK Se corrigieron {fixed_count} fincas')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('\nOK No se encontraron caracteres para corregir')
            )

