from django.db import models
from django.conf import settings
from core.models import BaseModel

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
    
    # Información de la acción
    admin = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='admin_actions',
        verbose_name='Administrador'
    )
    action_type = models.CharField(
        max_length=20,
        choices=ACTION_TYPES,
        verbose_name='Tipo de Acción'
    )
    object_type = models.CharField(
        max_length=20,
        choices=OBJECT_TYPES,
        verbose_name='Tipo de Objeto'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='ID del Objeto'
    )
    object_name = models.CharField(
        max_length=255,
        verbose_name='Nombre del Objeto'
    )
    
    # Detalles de la acción
    description = models.TextField(
        verbose_name='Descripción',
        help_text='Detalles de la acción realizada'
    )
    changes = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Cambios',
        help_text='Cambios específicos realizados (JSON)'
    )
    
    # Información técnica
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name='User Agent'
    )
    
    class Meta:
        verbose_name = 'Acción de Administrador'
        verbose_name_plural = 'Acciones de Administrador'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['admin', 'created_at']),
            models.Index(fields=['action_type', 'created_at']),
            models.Index(fields=['object_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.admin.username} - {self.get_action_type_display()} {self.get_object_type_display()}: {self.object_name}"

def log_admin_action(admin, action_type, object_type, object_name, description, object_id=None, changes=None, request=None):
    """Función helper para registrar acciones del administrador"""
    ip_address = '127.0.0.1'
    user_agent = None
    
    if request:
        ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    AdminAction.objects.create(
        admin=admin,
        action_type=action_type,
        object_type=object_type,
        object_id=object_id,
        object_name=object_name,
        description=description,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent
    )
