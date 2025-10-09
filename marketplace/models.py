from django.db import models
from django.conf import settings
from core.models import BaseModel, Farm
from inventory.models import Crop

# Create your models here.
class Publication(BaseModel):
    cultivo = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='publicaciones')
    finca = models.ForeignKey(Farm, on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name='publicaciones', verbose_name="Finca de Origen")
    
    # Campos de la publicación
    precio_por_unidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Unidad")
    cantidad_disponible = models.PositiveIntegerField(verbose_name="Cantidad Disponible")
    cantidad_minima = models.PositiveIntegerField(default=1, verbose_name="Cantidad Mínima de Venta")
    
    # Ubicación específica para esta publicación (puede diferir del perfil)
    departamento = models.CharField(max_length=100, verbose_name="Departamento de Origen", default='')
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad/Municipio de Origen", default='')
    
    # Categorización y estado
    CATEGORIA_CHOICES = [
        ('Frutas', 'Frutas'),
        ('Verduras', 'Verduras'),
        ('Hortalizas', 'Hortalizas'),
        ('Granos', 'Granos'),
        ('Tubérculos', 'Tubérculos'),
        ('Hierbas', 'Hierbas y Especias'),
        ('Otros', 'Otros'),
    ]
    categoria = models.CharField(max_length=50, choices=CATEGORIA_CHOICES, verbose_name="Categoría", default='Otros')
    
    ESTADO_CHOICES = [
        ('Activa', 'Activa'),
        ('Pausada', 'Pausada'),
        ('Agotada', 'Agotada'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Activa', verbose_name="Estado")
    
    descripcion = models.TextField(blank=True, verbose_name="Descripción Adicional", default='')
    
    imagen = models.ImageField(upload_to='publications/', blank=True, null=True, verbose_name="Imagen del Producto")

    @property
    def categoria_display(self):
        return self.get_categoria_display()

    @property
    def ciudad_display(self):
        return f"{self.ciudad}, {self.departamento}"

    def __str__(self):
        return f'{self.cultivo.nombre} por {self.cultivo.productor.username}'
