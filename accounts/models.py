from django.contrib.auth.models import AbstractUser
from django.db import models
from core.models import BaseModel
from core.colombia_locations import get_departments, get_all_cities

class User(AbstractUser):
    ROLE_CHOICES = (
        ('Admin', 'Admin'),
        ('Productor', 'Productor'),
        ('Comprador', 'Comprador'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, blank=True, null=True)
    cedula = models.CharField(max_length=20, null=True, blank=True, verbose_name="Cédula", help_text="Número de cédula de identidad")
    telefono = models.CharField(max_length=15, blank=True, null=True, verbose_name="Teléfono", help_text="Número de teléfono de contacto")
    profile_image = models.ImageField(upload_to='profile_images/', blank=True, null=True, verbose_name="Imagen de Perfil")
    
    # Ubicación
    departamento = models.CharField(max_length=100, blank=True, null=True, verbose_name="Departamento")
    ciudad = models.CharField(max_length=100, blank=True, null=True, verbose_name="Ciudad/Municipio")
    
    # Nuevo campo para sistema unificado
    can_sell = models.BooleanField(default=False, verbose_name="¿Puede vender?", help_text="Indica si el usuario puede crear publicaciones y vender productos")
    
    # Campos para manejo de autenticación dual
    has_password = models.BooleanField(default=True, help_text='Indica si el usuario tiene una contraseña configurada', verbose_name='Tiene contraseña')
    is_google_user = models.BooleanField(default=False, help_text='Indica si el usuario se registró con Google', verbose_name='Usuario de Google')


class Farm(BaseModel):
    """Modelo para representar las fincas de los vendedores"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='farms', verbose_name="Propietario")
    nombre = models.CharField(max_length=200, verbose_name="Nombre de la Finca")
    
    # Ubicación
    departamento = models.CharField(max_length=100, verbose_name="Departamento")
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad/Municipio")
    direccion = models.CharField(max_length=255, verbose_name="Dirección/Vereda", blank=True, null=True, 
                                help_text="Vereda, sector o dirección específica")
    
    # Información adicional
    descripcion = models.TextField(verbose_name="Descripción", blank=True, null=True, 
                                   help_text="Descripción de la finca, tipo de terreno, etc.")
    area = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Área (hectáreas)", 
                               blank=True, null=True, help_text="Área total de la finca en hectáreas")
    cultivos_principales = models.CharField(max_length=255, verbose_name="Cultivos Principales", 
                                           blank=True, null=True, 
                                           help_text="Principales cultivos de esta finca")
    
    # Estado
    activa = models.BooleanField(default=True, verbose_name="Finca Activa")
    
    class Meta:
        verbose_name = "Finca"
        verbose_name_plural = "Fincas"
        ordering = ['-created_at']
        unique_together = ['user', 'nombre']  # Un usuario no puede tener dos fincas con el mismo nombre
    
    def __str__(self):
        return f"{self.nombre} - {self.user.get_full_name() or self.user.username}"
    
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

class ProducerProfile(BaseModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='producer_profile')
    
    # Ubicación estructurada (TODOS OPCIONALES)
    departamento = models.CharField(max_length=100, verbose_name="Departamento", blank=True, null=True)
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad/Municipio", blank=True, null=True)
    direccion = models.CharField(max_length=255, verbose_name="Dirección específica", blank=True, null=True,
                               help_text="Ej: Vereda, finca, sector específico")
    
    # Campos existentes (mantener compatibilidad) - TODOS OPCIONALES
    location = models.CharField(max_length=255, blank=True, null=True,
                              help_text="Campo legacy - se actualizará automáticamente")
    farm_description = models.TextField(verbose_name="Descripción de la Finca", blank=True, null=True)
    main_crops = models.CharField(max_length=255, verbose_name="Cultivos Principales", blank=True, null=True)

    # Estadísticas de ventas (movidas desde sales.UserProfile)
    total_ventas = models.IntegerField(default=0, verbose_name="Total de Ventas")
    ingresos_totales = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                         verbose_name="Ingresos Totales")
    calificacion_promedio = models.DecimalField(
        max_digits=3, decimal_places=2, default=0, 
        verbose_name="Calificación Promedio como Vendedor"
    )
    total_calificaciones = models.IntegerField(default=0, verbose_name="Total de Calificaciones Recibidas")
    fecha_primera_venta = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Primera Venta")

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
    company_name = models.CharField(max_length=255, verbose_name="Nombre de la Empresa", blank=True, null=True)
    business_type = models.CharField(max_length=255, verbose_name="Tipo de Negocio", blank=True, null=True)
    
    # Ubicación (TODOS OPCIONALES)
    departamento = models.CharField(max_length=100, verbose_name="Departamento", blank=True, null=True)
    ciudad = models.CharField(max_length=100, verbose_name="Ciudad/Municipio", blank=True, null=True)

    # Estadísticas de compras (movidas desde sales.UserProfile)
    total_compras = models.IntegerField(default=0, verbose_name="Total de Compras")
    gastos_totales = models.DecimalField(max_digits=12, decimal_places=2, default=0, 
                                       verbose_name="Gastos Totales")
    fecha_primera_compra = models.DateTimeField(null=True, blank=True, verbose_name="Fecha de Primera Compra")

    @property
    def ciudad_departamento(self):
        """Retorna ciudad y departamento"""
        if self.ciudad and self.departamento:
            return f"{self.ciudad}, {self.departamento}"
        return "Ubicación no especificada"

    def __str__(self):
        return self.user.username

class AdminAction(BaseModel):
    """Modelo para registrar acciones del administrador"""
    ACTION_TYPES = (
        ('create', 'Crear'),
        ('update', 'Actualizar'),
        ('delete', 'Eliminar'),
        ('login', 'Inicio de sesión'),
        ('logout', 'Cerrar sesión'),
        ('view', 'Ver'),
        ('export', 'Exportar'),
        ('import', 'Importar'),
    )
    
    OBJECT_TYPES = (
        ('user', 'Usuario'),
        ('crop', 'Cultivo'),
        ('publication', 'Publicación'),
        ('order', 'Pedido'),
        ('farm', 'Finca'),
        ('system', 'Sistema'),
    )
    
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name='admin_actions', verbose_name="Administrador")
    action_type = models.CharField(max_length=20, choices=ACTION_TYPES, verbose_name="Tipo de Acción")
    object_type = models.CharField(max_length=20, choices=OBJECT_TYPES, verbose_name="Tipo de Objeto")
    object_id = models.PositiveIntegerField(blank=True, null=True, verbose_name="ID del Objeto")
    object_name = models.CharField(max_length=255, verbose_name="Nombre del Objeto")
    description = models.TextField(verbose_name="Descripción", help_text="Detalles de la acción realizada")
    changes = models.JSONField(null=True, blank=True, verbose_name="Cambios", help_text="Cambios específicos realizados (JSON)")
    ip_address = models.GenericIPAddressField(verbose_name="Dirección IP")
    user_agent = models.TextField(blank=True, null=True, verbose_name="User Agent")
    
    class Meta:
        verbose_name = "Acción de Administrador"
        verbose_name_plural = "Acciones de Administrador"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['object_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.get_action_type_display()} {self.get_object_type_display()}: {self.object_name}"


class PasswordResetCode(BaseModel):
    """Modelo para códigos de recuperación de contraseña con expiración"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='password_reset_codes', verbose_name="Usuario")
    code = models.CharField(max_length=6, verbose_name="Código de Recuperación")
    email = models.EmailField(verbose_name="Email")
    is_used = models.BooleanField(default=False, verbose_name="Código Usado")
    expires_at = models.DateTimeField(verbose_name="Expira en")
    
    class Meta:
        verbose_name = "Código de Recuperación"
        verbose_name_plural = "Códigos de Recuperación"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code', 'is_used']),
            models.Index(fields=['email', 'is_used']),
            models.Index(fields=['expires_at']),
        ]
    
    def is_expired(self):
        """Verifica si el código ha expirado"""
        from django.utils import timezone
        return timezone.now() > self.expires_at
    
    def is_valid(self):
        """Verifica si el código es válido (no usado y no expirado)"""
        return not self.is_used and not self.is_expired()
    
    def __str__(self):
        return f"Código {self.code} para {self.user.email} - {'Válido' if self.is_valid() else 'Inválido'}"
