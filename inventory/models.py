from django.db import models
from django.conf import settings
from core.models import BaseModel

class Crop(BaseModel):
    CATEGORIA_CHOICES = (
        ('hortalizas', 'Hortalizas'),
        ('frutas', 'Frutas'),
        ('cereales_granos', 'Cereales y Granos'),
        ('leguminosas', 'Leguminosas'),
        ('tuberculos', 'Tubérculos'),
        ('hierbas_aromaticas', 'Hierbas Aromáticas'),
        ('otros', 'Otros'),
    )
    ESTADO_CHOICES = (
        ('sembrado', 'Sembrado'),
        ('en_crecimiento', 'En Crecimiento'),
        ('listo_para_cosechar', 'Listo para Cosecha'),
        ('cosechado', 'Cosechado'),
    )
    
    UNIDAD_CHOICES = (
        ('kg', 'Kilogramos (kg)'),
        ('toneladas', 'Toneladas'),
        ('libras', 'Libras'),
        ('unidades', 'Unidades'),
        ('cajas', 'Cajas'),
        ('bultos', 'Bultos'),
        ('arrobas', 'Arrobas'),
    )
    
    # Información del producto
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Cultivo")
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES, default='otros', verbose_name="Categoría")
    
    # Información del productor
    productor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                related_name='cultivos', verbose_name="Productor", null=True)
    
    # Información de cantidad y medida
    cantidad_estimada = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          verbose_name="Cantidad Estimada")
    unidad_medida = models.CharField(max_length=20, choices=UNIDAD_CHOICES, default='kg',
                                   verbose_name="Unidad de Medida")
    
    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='sembrado',
                            verbose_name="Estado del Cultivo")
    fecha_disponibilidad = models.DateField(null=True, blank=True, verbose_name="Disponible Desde")

    imagen = models.ImageField(upload_to='crops/', blank=True, null=True, verbose_name="Imagen del Cultivo")

    # Información adicional
    notas = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales",
                           help_text="Información adicional sobre el cultivo")

    class Meta:
        verbose_name = "Cultivo"
        verbose_name_plural = "Cultivos"
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.cantidad_estimada} {self.unidad_medida} de {self.nombre} - {self.productor.first_name}'
