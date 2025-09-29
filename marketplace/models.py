from django.db import models
from core.models import BaseModel
from inventory.models import Crop

# Create your models here.

class Publication(BaseModel):
    ESTADO_CHOICES = (
        ('disponible', 'Disponible'),
        ('vendido', 'Vendido'),
        ('pausado', 'Pausado'),
        ('agotado', 'Agotado'),
    )
    
    # Relación con el cultivo
    cultivo = models.ForeignKey(Crop, on_delete=models.CASCADE, 
                                 verbose_name="Cultivo", related_name='publicaciones')
    
    # Información de precio y cantidad
    precio_por_unidad = models.DecimalField(max_digits=10, decimal_places=2, 
                                          verbose_name="Precio por Unidad ($)")
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2, 
                                            verbose_name="Cantidad Disponible")
    cantidad_minima = models.DecimalField(max_digits=10, decimal_places=2, default=1,
                                        verbose_name="Cantidad Mínima de Pedido")
    
    # Estado y descripción
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, 
                            default='disponible', verbose_name="Estado")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción",
                                 help_text="Describe la calidad, características especiales, etc.")

    class Meta:
        verbose_name = "Publicación"
        verbose_name_plural = "Publicaciones"
        ordering = ['-created_at']

    def __str__(self):
        return f'Publicación: {self.cultivo.nombre_producto} - {self.cultivo.productor.first_name}'
