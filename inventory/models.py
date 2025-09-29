from django.db import models
from django.conf import settings
from core.models import BaseModel

class Product(BaseModel):
    CATEGORIA_CHOICES = (
        ('hortalizas', 'Hortalizas'),
        ('frutas', 'Frutas'),
        ('cereales_granos', 'Cereales y Granos'),
        ('leguminosas', 'Leguminosas'),
        ('tuberculos', 'Tubérculos'),
        ('hierbas_aromaticas', 'Hierbas Aromáticas'),
        ('otros', 'Otros'),
    )
    
    nombre = models.CharField(max_length=100, unique=True, verbose_name="Nombre del Producto")
    categoria = models.CharField(max_length=30, choices=CATEGORIA_CHOICES, 
                               default='otros', verbose_name="Categoría")
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True, 
                             verbose_name="Imagen del Producto")

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ['categoria', 'nombre']

    def __str__(self):
        return self.nombre

class Crop(BaseModel):
    ESTADO_CHOICES = (
        ('sembrado', 'Sembrado'),
        ('en_crecimiento', 'En Crecimiento'),
        ('listo_cosecha', 'Listo para Cosecha'),
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
    producto = models.ForeignKey(Product, on_delete=models.CASCADE, 
                                 related_name='cultivos', verbose_name="Tipo de Producto")
    
    # Información del productor
    productor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, 
                                related_name='cultivos', verbose_name="Productor")
    
    # Información de cantidad y medida
    cantidad_estimada = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          verbose_name="Cantidad Estimada")
    unidad_medida = models.CharField(max_length=20, choices=UNIDAD_CHOICES, default='kg',
                                   verbose_name="Unidad de Medida")
    
    # Estado y fechas
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='sembrado',
                            verbose_name="Estado del Cultivo")
    fecha_disponibilidad = models.DateField(verbose_name="Fecha Estimada de Disponibilidad", null=True, blank=True)
    
    # Información adicional
    notas = models.TextField(blank=True, null=True, verbose_name="Notas Adicionales",
                           help_text="Información adicional sobre el cultivo")

    class Meta:
        verbose_name = "Cultivo"
        verbose_name_plural = "Cultivos"
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.cantidad_estimada} {self.unidad_medida} de {self.producto.nombre} - {self.productor.first_name}'
