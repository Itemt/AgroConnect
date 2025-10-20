from django.db import models
from django.conf import settings
from core.models import BaseModel, Farm
from inventory.models import Crop

# Create your models here.
class Publication(BaseModel):
    cultivo = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='publicaciones')
    finca = models.ForeignKey(Farm, on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name='publicaciones', verbose_name="Finca de Origen")
    
    # Unidad de medida para venta
    UNIDAD_CHOICES = [
        # Medidas de peso (convertibles)
        ('kg', 'Kilogramos (kg)'),
        ('g', 'Gramos (g)'),
        ('libras', 'Libras (lb)'),
        ('arrobas', 'Arrobas (@)'),
        ('toneladas', 'Toneladas (t)'),
        # Medidas discretas (NO convertibles)
        ('unidades', 'Unidades (fijo)'),
        ('cajas', 'Cajas (fijo)'),
        ('bultos', 'Bultos/Sacos (fijo)'),
    ]
    
    # Unidades que NO permiten conversión
    UNIDADES_NO_CONVERTIBLES = ['unidades', 'cajas', 'bultos']
    
    # Campos de la publicación
    unidad_medida = models.CharField(max_length=20, choices=UNIDAD_CHOICES, default='kg',
                                     verbose_name="Unidad de Medida")
    precio_por_unidad = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio por Unidad")
    cantidad_disponible = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Cantidad Disponible")
    cantidad_minima = models.DecimalField(max_digits=10, decimal_places=2, default=1, verbose_name="Cantidad Mínima de Venta")
    
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

    # Tabla de conversión a kilogramos (unidad base)
    # Solo para unidades de peso
    CONVERSION_TO_KG = {
        'kg': 1,
        'g': 0.001,
        'libras': 0.453592,
        'arrobas': 11.502,  # 1 arroba = 25 libras = 11.502 kg
        'toneladas': 1000,
        # Unidades discretas no tienen conversión
        'unidades': None,
        'cajas': None,
        'bultos': None,
    }
    
    @staticmethod
    def convertir_unidad(cantidad, unidad_origen, unidad_destino):
        """
        Convierte una cantidad de una unidad a otra.
        Retorna cantidad_convertida o None si no es posible
        """
        # Si son la misma unidad, no hay conversión
        if unidad_origen == unidad_destino:
            return float(cantidad)
        
        # Obtener factores de conversión
        factor_origen = Publication.CONVERSION_TO_KG.get(unidad_origen)
        factor_destino = Publication.CONVERSION_TO_KG.get(unidad_destino)
        
        # Si alguna unidad no es convertible, retornar None
        if factor_origen is None or factor_destino is None:
            return None
        
        # Convertir a kg primero, luego a unidad destino
        cantidad_kg = float(cantidad) * factor_origen
        cantidad_convertida = cantidad_kg / factor_destino
        
        return round(cantidad_convertida, 3)
    
    def obtener_precio_en_unidad(self, unidad_destino):
        """
        Retorna el precio por unidad convertido a la unidad destino.
        Ejemplo: Si vendo a $50,000/arroba y convierto a kg:
        1 arroba = 11.502 kg
        Precio por kg = $50,000 / 11.502 = $4,346/kg
        """
        if self.unidad_medida == unidad_destino:
            return float(self.precio_por_unidad)
        
        # Convertir 1 unidad de origen a unidad destino
        cantidad_convertida = self.convertir_unidad(1, self.unidad_medida, unidad_destino)
        if cantidad_convertida is None:
            return None
        
        # Precio en nueva unidad = precio original / cuántas unidades destino hay en 1 unidad origen
        precio_convertido = float(self.precio_por_unidad) / cantidad_convertida
        return round(precio_convertido, 2)
    
    def es_unidad_convertible(self):
        """
        Retorna True si la unidad de esta publicación permite conversión.
        False si es una unidad discreta (unidades, cajas, bultos).
        """
        return self.unidad_medida not in self.UNIDADES_NO_CONVERTIBLES
    
    def unidades_disponibles_para_conversion(self):
        """
        Retorna las unidades a las que se puede convertir esta publicación.
        Si es unidad NO convertible, solo retorna la misma unidad.
        """
        if not self.es_unidad_convertible():
            return [self.unidad_medida]
        
        # Solo retornar unidades de peso (convertibles)
        return [u for u, f in self.CONVERSION_TO_KG.items() if f is not None]
    
    def verificar_disponibilidad(self, cantidad_solicitada, unidad_solicitada):
        """
        Verifica si hay suficiente cantidad disponible.
        Convierte la cantidad solicitada a la unidad del vendedor para comparar.
        
        Retorna (disponible: bool, cantidad_disponible_en_unidad_solicitada: float)
        """
        # Convertir cantidad solicitada a la unidad del vendedor
        cantidad_en_unidad_vendedor = self.convertir_unidad(
            cantidad_solicitada, 
            unidad_solicitada, 
            self.unidad_medida
        )
        
        if cantidad_en_unidad_vendedor is None:
            return False, 0
        
        # Verificar si hay suficiente
        disponible = cantidad_en_unidad_vendedor <= float(self.cantidad_disponible)
        
        # Convertir cantidad disponible a la unidad solicitada para mostrar al usuario
        cantidad_disponible_convertida = self.convertir_unidad(
            self.cantidad_disponible,
            self.unidad_medida,
            unidad_solicitada
        )
        
        return disponible, cantidad_disponible_convertida

    @property
    def categoria_display(self):
        return self.get_categoria_display()

    @property
    def ciudad_display(self):
        return f"{self.ciudad}, {self.departamento}"

    def __str__(self):
        return f'{self.cultivo.nombre} por {self.cultivo.productor.username}'
