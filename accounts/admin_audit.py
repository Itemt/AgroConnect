"""
Funciones helper para registrar acciones del administrador
"""
from django.contrib.auth import get_user_model
from django.http import HttpRequest
from .models import AdminAction

User = get_user_model()


def get_client_ip(request):
    """Obtiene la IP del cliente desde el request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Obtiene el User Agent del cliente"""
    return request.META.get('HTTP_USER_AGENT', '')


def log_admin_action(
    admin_user,
    action_type,
    object_type,
    object_name,
    description,
    request=None,
    object_id=None,
    changes=None
):
    """
    Registra una acción del administrador
    
    Args:
        admin_user: Usuario administrador que realiza la acción
        action_type: Tipo de acción (create, update, delete, etc.)
        object_type: Tipo de objeto (user, crop, order, etc.)
        object_name: Nombre del objeto afectado
        description: Descripción de la acción
        request: Request HTTP (opcional, para obtener IP y User Agent)
        object_id: ID del objeto (opcional)
        changes: Diccionario con los cambios realizados (opcional)
    """
    ip_address = '127.0.0.1'  # Default IP
    user_agent = 'System'  # Default user agent
    
    if request:
        ip_address = get_client_ip(request) or '127.0.0.1'
        user_agent = get_user_agent(request) or 'System'
    
    AdminAction.objects.create(
        admin=admin_user,
        action_type=action_type,
        object_type=object_type,
        object_id=object_id,
        object_name=object_name,
        description=description,
        changes=changes,
        ip_address=ip_address,
        user_agent=user_agent
    )


def log_user_action(admin_user, action_type, user, request=None, changes=None):
    """Registra una acción relacionada con un usuario"""
    log_admin_action(
        admin_user=admin_user,
        action_type=action_type,
        object_type='user',
        object_id=user.id,
        object_name=f"{user.get_full_name() or user.username} ({user.email})",
        description=f"{action_type.title()} usuario: {user.username}",
        request=request,
        changes=changes
    )


def log_order_action(admin_user, action_type, order, request=None, changes=None):
    """Registra una acción relacionada con un pedido"""
    log_admin_action(
        admin_user=admin_user,
        action_type=action_type,
        object_type='order',
        object_id=order.id,
        object_name=f"Pedido #{order.id} - {order.publicacion.cultivo.nombre if order.publicacion else 'N/A'}",
        description=f"{action_type.title()} pedido #{order.id}",
        request=request,
        changes=changes
    )


def log_crop_action(admin_user, action_type, crop, request=None, changes=None):
    """Registra una acción relacionada con un cultivo"""
    log_admin_action(
        admin_user=admin_user,
        action_type=action_type,
        object_type='crop',
        object_id=crop.id,
        object_name=f"{crop.nombre} - {crop.productor.username}",
        description=f"{action_type.title()} cultivo: {crop.nombre}",
        request=request,
        changes=changes
    )


def log_publication_action(admin_user, action_type, publication, request=None, changes=None):
    """Registra una acción relacionada con una publicación"""
    log_admin_action(
        admin_user=admin_user,
        action_type=action_type,
        object_type='publication',
        object_id=publication.id,
        object_name=f"{publication.cultivo.nombre} - {publication.cultivo.productor.username}",
        description=f"{action_type.title()} publicación: {publication.cultivo.nombre}",
        request=request,
        changes=changes
    )


def log_farm_action(admin_user, action_type, farm, request=None, changes=None):
    """Registra una acción relacionada con una finca"""
    log_admin_action(
        admin_user=admin_user,
        action_type=action_type,
        object_type='farm',
        object_id=farm.id,
        object_name=f"{farm.nombre} - {farm.propietario.username}",
        description=f"{action_type.title()} finca: {farm.nombre}",
        request=request,
        changes=changes
    )
