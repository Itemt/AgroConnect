from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel
from core.colombia_locations import get_departments, get_all_cities

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Productor', 'Productor'),
        ('Comprador', 'Comprador'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, null=True)

class ProducerProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='producer_profile')
    
    # Ubicación estructurada
    departamento = models.CharField(max_length=100, verbose_name="Departamento", blank=True)
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad/Municipio", blank=True)
    direccion = models.CharField(max_length=255, verbose_name="Dirección específica", blank=True, 
                               help_text="Ej: Vereda, finca, sector específico")
    
    # Campos existentes (mantener compatibilidad)
    location = models.CharField(max_length=255, blank=True, 
                              help_text="Campo legacy - se actualizará automáticamente")
    farm_description = models.TextField(verbose_name="Descripción de la Finca")
    main_crops = models.CharField(max_length=255, verbose_name="Cultivos Principales")

    def save(self, *args, **kwargs):
        # Actualizar location automáticamente para compatibilidad
        if self.departamento and self.ciudad:
            location_parts = [self.ciudad, self.departamento]
            if self.direccion:
                location_parts.insert(0, self.direccion)
            self.location = ", ".join(location_parts)
        super().save(*args, **kwargs)

    @property
    def ubicacion_completa(self):
        """Retorna la ubicación completa formateada"""
        parts = []
        if self.direccion:
            parts.append(self.direccion)
        if self.ciudad:
            parts.append(self.ciudad)
        if self.departamento:
            parts.append(self.departamento)
        return ", ".join(parts) if parts else "Ubicación no especificada"

    @property
    def ciudad_departamento(self):
        """Retorna ciudad y departamento"""
        if self.ciudad and self.departamento:
            return f"{self.ciudad}, {self.departamento}"
        return "Ubicación no especificada"

    def __str__(self):
        return self.user.username

class BuyerProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='buyer_profile')
    company_name = models.CharField(max_length=255, verbose_name="Nombre de la Empresa")
    business_type = models.CharField(max_length=255, verbose_name="Tipo de Negocio")
    
    # Ubicación
    departamento = models.CharField(max_length=100, verbose_name="Departamento", blank=True)
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad/Municipio", blank=True)

    @property
    def ciudad_departamento(self):
        """Retorna ciudad y departamento"""
        if self.ciudad and self.departamento:
            return f"{self.ciudad}, {self.departamento}"
        return "Ubicación no especificada"

    def __str__(self):
        return self.user.username
