from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Notification(BaseModel):
    CATEGORY_CHOICES = (
        ('order', 'Pedido'),
        ('payment', 'Pago'),
        ('system', 'Sistema'),
    )

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Destinatario'
    )
    title = models.CharField(max_length=255, verbose_name='Título')
    message = models.TextField(verbose_name='Mensaje')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='system', verbose_name='Categoría')
    is_read = models.BooleanField(default=False, verbose_name='Leída')
    read_at = models.DateTimeField(null=True, blank=True, verbose_name='Leída el')

    # Referencias opcionales
    order_id = models.IntegerField(null=True, blank=True, verbose_name='ID Pedido')
    payment_id = models.IntegerField(null=True, blank=True, verbose_name='ID Pago')

    class Meta:
        verbose_name = 'Notificación'
        verbose_name_plural = 'Notificaciones'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} -> {self.recipient}"


# Helper to create and emit notifications via Channels
def create_notification(*, recipient, title, message, category='system', order_id=None, payment_id=None):
    """Crear notificación simple (sin WebSockets)"""
    notification = Notification.objects.create(
        recipient=recipient,
        title=title,
        message=message,
        category=category,
        order_id=order_id,
        payment_id=payment_id,
    )
    return notification


class Farm(BaseModel):
    """Modelo para gestionar las fincas de los productores"""
    
    TIPO_SUELO_CHOICES = (
        ('arcilloso', 'Arcilloso'),
        ('arenoso', 'Arenoso'),
        ('limoso', 'Limoso'),
        ('franco', 'Franco'),
        ('orgánico', 'Orgánico'),
        ('mixto', 'Mixto'),
    )
    
    TIPO_RIEGO_CHOICES = (
        ('natural', 'Natural (Lluvia)'),
        ('goteo', 'Goteo'),
        ('aspersión', 'Aspersión'),
        ('inundación', 'Inundación'),
        ('mixto', 'Mixto'),
    )
    
    # Información básica
    nombre = models.CharField(max_length=255, verbose_name="Nombre de la Finca")
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='fincas',
        verbose_name="Propietario"
    )
    descripcion = models.TextField(blank=True, null=True, verbose_name="Descripción")
    
    # Ubicación
    departamento = models.CharField(max_length=100, verbose_name="Departamento")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad/Municipio")
    direccion = models.TextField(verbose_name="Dirección")
    coordenadas_lat = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True,
        verbose_name="Latitud"
    )
    coordenadas_lng = models.DecimalField(
        max_digits=10, 
        decimal_places=7, 
        null=True, 
        blank=True,
        verbose_name="Longitud"
    )
    
    # Características de la finca
    area_total = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Área Total (hectáreas)"
    )
    area_cultivable = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        validators=[MinValueValidator(0.01)],
        verbose_name="Área Cultivable (hectáreas)"
    )
    tipo_suelo = models.CharField(
        max_length=20, 
        choices=TIPO_SUELO_CHOICES, 
        verbose_name="Tipo de Suelo"
    )
    tipo_riego = models.CharField(
        max_length=20, 
        choices=TIPO_RIEGO_CHOICES, 
        verbose_name="Tipo de Riego"
    )
    
    # Certificaciones
    certificacion_organica = models.BooleanField(default=False, verbose_name="Certificación Orgánica")
    certificacion_bpa = models.BooleanField(default=False, verbose_name="Certificación BPA")
    otras_certificaciones = models.TextField(blank=True, null=True, verbose_name="Otras Certificaciones")
    
    # Estado
    activa = models.BooleanField(default=True, verbose_name="Finca Activa")
    
    class Meta:
        verbose_name = "Finca"
        verbose_name_plural = "Fincas"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.nombre} - {self.propietario.username}"
    
    @property
    def ubicacion_completa(self):
        return f"{self.ciudad}, {self.departamento}"
    
    @property
    def area_disponible(self):
        return self.area_cultivable - self.area_ocupada
    
    @property
    def area_ocupada(self):
        from inventory.models import Crop
        return Crop.objects.filter(finca=self).aggregate(
            total=models.Sum('area_ocupada')
        )['total'] or 0
