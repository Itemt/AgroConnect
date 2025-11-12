from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.core.paginator import Paginator
from .models import Conversation, Message, Order, Rating
from marketplace.models import Publication
from .forms import MessageForm, OrderForm, OrderUpdateForm, RatingForm, OrderConfirmReceiptForm, OrderSearchForm
from accounts.models import ProducerProfile, BuyerProfile
from django.views.decorators.http import require_POST
from cart.models import Cart
from core.models import create_notification
from core.models import Notification
from .qr_utils import get_order_buyer_qr, get_order_seller_qr
import logging

logger = logging.getLogger(__name__)

# Create your views here.

@login_required
def create_order_view(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)

    if request.user == publication.cultivo.productor:
        # Redirigir si es el dueño de la publicación (no puede comprarse a sí mismo)
        messages.error(request, 'No puedes comprar tu propio producto.')
        return redirect('publication_detail', publication_id=publication.id)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.publicacion = publication
            order.comprador = request.user
            
            # Calcular precio final
            order.precio_total = order.cantidad_acordada * publication.precio_por_unidad
            order.estado = 'pendiente'  # Estado inicial
            
            # Validar que la cantidad no exceda la disponible
            if order.cantidad_acordada > publication.cantidad_disponible:
                form.add_error('cantidad_acordada', 'La cantidad solicitada excede la disponible.')
            else:
                # Actualizar la cantidad disponible en la publicación
                publication.cantidad_disponible -= order.cantidad_acordada
                publication.save()
                
            order.save()
            # Notificar al vendedor que hay un nuevo pedido
            create_notification(
                recipient=publication.cultivo.productor,
                title='Nuevo pedido recibido',
                message=f'El comprador {request.user.first_name} ha creado el pedido #{order.id} de {order.cantidad_acordada} unidades.',
                category='order',
                order_id=order.id,
            )
            messages.success(request, 'Pedido creado exitosamente. El vendedor será notificado.')
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()

    context = {
        'form': form,
        'publication': publication
    }
    return render(request, 'sales/order_form.html', context)


@login_required
def order_history_view(request):
    """Vista mejorada del historial de pedidos con filtros"""
    form = OrderSearchForm(request.GET)
    
    if request.user.role == 'Comprador':
        orders = Order.objects.filter(comprador=request.user)
    elif request.user.role == 'Productor':
        # Los productores también pueden ser compradores, mostrar sus compras
        orders = Order.objects.filter(comprador=request.user)
    else:
        orders = Order.objects.none()

    # Aplicar filtros
    if form.is_valid():
        search = form.cleaned_data.get('search')
        estado = form.cleaned_data.get('estado')
        fecha_desde = form.cleaned_data.get('fecha_desde')
        fecha_hasta = form.cleaned_data.get('fecha_hasta')
        
        if search:
            orders = orders.filter(
                Q(publicacion__cultivo__nombre__icontains=search) |
                Q(comprador__first_name__icontains=search) |
                Q(comprador__last_name__icontains=search) |
                Q(publicacion__cultivo__productor__first_name__icontains=search) |
                Q(publicacion__cultivo__productor__last_name__icontains=search)
            )
        
        if estado:
            orders = orders.filter(estado=estado)
        
        if fecha_desde:
            orders = orders.filter(created_at__date__gte=fecha_desde)
        
        if fecha_hasta:
            orders = orders.filter(created_at__date__lte=fecha_hasta)

    orders = orders.select_related(
        'publicacion__cultivo', 'publicacion__cultivo__productor', 'comprador'
    ).order_by('-created_at')

    # Agregar acciones disponibles para cada pedido
    orders_with_actions = []
    for order in orders:
        order.available_actions = order.get_available_actions_for_user(request.user)
        orders_with_actions.append(order)

    # Paginación
    paginator = Paginator(orders_with_actions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'orders': page_obj,
        'form': form,
        'user_role': request.user.role
    }
    
    # Render different template based on user role to keep appropriate sidebar
    if request.user.role == 'Productor':
        return render(request, 'sales/order_history_producer.html', context)
    else:
        return render(request, 'sales/order_history_buyer.html', context)


def order_detail_qr_view(request, token):
    """
    Vista para acceder al detalle del pedido mediante QR code
    No requiere autenticación ya que el token es único y seguro
    """
    try:
        # Buscar el pedido por el token (puede ser de comprador o vendedor)
        order = Order.objects.filter(
            Q(token_comprador=token) | Q(token_vendedor=token)
        ).select_related(
            'publicacion__cultivo__productor', 'comprador'
        ).first()
        
        if not order:
            messages.error(request, 'Código QR inválido o pedido no encontrado.')
            return render(request, '404.html', status=404)
        
        # Determinar el tipo de usuario que está accediendo
        is_buyer_qr = str(order.token_comprador) == str(token)
        is_seller_qr = str(order.token_vendedor) == str(token)
        
        # Obtener calificaciones existentes
        rating_from_buyer = order.calificaciones.filter(tipo='comprador_a_vendedor').first()
        rating_from_seller = order.calificaciones.filter(tipo='vendedor_a_comprador').first()
        
        # Obtener el payment asociado al order
        payment = None
        try:
            payment = order.payment
        except:
            pass
        
        # Generar códigos QR
        buyer_qr = get_order_buyer_qr(order) if is_buyer_qr else None
        seller_qr = get_order_seller_qr(order) if is_seller_qr else None
        
        context = {
            'order': order,
            'payment': payment,
            'rating_from_buyer': rating_from_buyer,
            'rating_from_seller': rating_from_seller,
            'is_buyer_qr': is_buyer_qr,
            'is_seller_qr': is_seller_qr,
            'buyer_qr_code': buyer_qr,
            'seller_qr_code': seller_qr,
            'accessed_via_qr': True,
        }
        
        return render(request, 'sales/order_detail_qr.html', context)
        
    except Exception as e:
        logger.error(f"Error accediendo al pedido por QR: {e}")
        messages.error(request, 'Error al acceder al pedido.')
        return render(request, '404.html', status=404)


@login_required
def order_detail_view(request, order_id):
    """Vista detallada de un pedido"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Verificar que el usuario tenga acceso a este pedido
    if not (request.user == order.comprador or request.user == order.vendedor):
        messages.error(request, 'No tienes acceso a este pedido.')
        return redirect('order_history')
    
    # Obtener calificaciones existentes
    rating_from_buyer = order.calificaciones.filter(tipo='comprador_a_vendedor').first()
    rating_from_seller = order.calificaciones.filter(tipo='vendedor_a_comprador').first()
    
    # Obtener la calificación del usuario actual si existe (para editar)
    my_rating = None
    if request.user == order.vendedor:
        my_rating = rating_from_seller
    elif request.user == order.comprador:
        my_rating = rating_from_buyer
    
    # Agregar acciones disponibles
    order.available_actions = order.get_available_actions_for_user(request.user)
    
    # Importar settings para verificar modo test
    from django.conf import settings
    
    # Obtener el payment asociado al order
    payment = None
    try:
        payment = order.payment
    except:
        pass
    
    # Generar códigos QR
    buyer_qr = get_order_buyer_qr(order) if request.user == order.comprador else None
    seller_qr = get_order_seller_qr(order) if request.user == order.vendedor else None
    
    context = {
        'order': order,
        'payment': payment,
        'rating_from_buyer': rating_from_buyer,
        'rating_from_seller': rating_from_seller,
        'my_rating': my_rating,
        'user_role': request.user.role,
        'buyer_qr_code': buyer_qr,
        'seller_qr_code': seller_qr,
    }
    
    # Render different template based on user role to keep appropriate sidebar
    if request.user.role == 'Productor':
        return render(request, 'sales/order_detail_producer.html', context)
    else:
        return render(request, 'sales/order_detail_buyer.html', context)


@login_required
def quick_update_order_status_view(request, order_id):
    """Vista para actualización rápida de estado (inline desde el historial)"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Solo el vendedor puede actualizar el estado
    if request.user != order.vendedor:
        messages.error(request, 'No tienes permisos para actualizar este pedido.')
        return redirect('producer_sales')
    
    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado')
        
        # Si el nuevo estado es 'enviado', redirigir a la página especial
        if nuevo_estado == 'enviado':
            # Si es una petición AJAX, devolver JSON con redirección
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'redirect': f'/order/{order.id}/mark-shipped/',
                    'message': 'Redirigiendo a página de envío...'
                })
            else:
                return redirect('mark_order_shipped', order_id=order.id)
        
        # Validar que el estado es válido y el vendedor puede cambiarlo
        estados_validos = {
            'pendiente': ['confirmado', 'cancelado'],
            'confirmado': ['en_preparacion', 'cancelado'],
            'en_preparacion': [],  # enviado debe ir por la página especial
            'enviado': ['en_transito'],
            'en_transito': [],
        }
        
        if nuevo_estado in estados_validos.get(order.estado, []):
            order.estado = nuevo_estado
            
            # Actualizar fechas según el estado
            if nuevo_estado == 'confirmado' and not order.fecha_confirmacion:
                order.fecha_confirmacion = timezone.now()
            
            order.save()
            # Notificar al comprador sobre el cambio de estado
            create_notification(
                recipient=order.comprador,
                title='Estado de pedido actualizado',
                message=f'Tu pedido #{order.id} ahora está: {order.get_estado_display()}.',
                category='order',
                order_id=order.id,
            )
            return JsonResponse({
                'success': True,
                'message': f'Estado actualizado a: {order.get_estado_display()}',
                'new_status': order.estado,
                'new_status_display': order.get_estado_display()
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Estado no válido para esta transición.'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Método no permitido.'
    })


@login_required
def mark_order_shipped_view(request, order_id):
    """Vista especial para marcar pedido como enviado con notas y fecha de entrega"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Solo el vendedor puede marcar como enviado
    if request.user != order.vendedor:
        messages.error(request, 'No tienes permisos para actualizar este pedido.')
        return redirect('producer_sales')
    
    # Verificar que el pedido puede ser marcado como enviado
    if order.estado not in ['confirmado', 'en_preparacion']:
        messages.error(request, 'Este pedido no puede ser marcado como enviado en su estado actual.')
        return redirect('producer_sales')
    
    if request.method == 'POST':
        from .forms import OrderShipmentForm
        form = OrderShipmentForm(request.POST)
        if form.is_valid():
            # Cambiar automáticamente a 'en_transito' después de enviado
            order.estado = 'en_transito'
            order.fecha_envio = timezone.now()
            
            # Agregar notas del vendedor si existen
            notas = form.cleaned_data.get('notas_vendedor')
            if notas:
                if order.notas_vendedor:
                    order.notas_vendedor += f"\n\n[Envío] {notas}"
                else:
                    order.notas_vendedor = f"[Envío] {notas}"
            
            order.save()
            # Notificar al comprador que el pedido está en tránsito
            create_notification(
                recipient=order.comprador,
                title='Pedido en tránsito',
                message=f'Tu pedido #{order.id} está en tránsito. Debería llegar en 3-5 días hábiles.',
                category='order',
                order_id=order.id,
            )
            messages.success(request, 'Pedido marcado como enviado exitosamente.')
            return redirect('producer_sales')
    else:
        from .forms import OrderShipmentForm
        form = OrderShipmentForm()
    
    context = {
        'form': form,
        'order': order
    }
    return render(request, 'sales/mark_shipped.html', context)



@login_required
def confirm_order_receipt_view(request, order_id):
    """Vista unificada para confirmar recepción y calificar el pedido"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Solo el comprador puede confirmar la recepción
    if request.user != order.comprador:
        messages.error(request, 'No tienes permisos para confirmar este pedido.')
        return redirect('order_detail', order_id=order.id)
    
    # Verificar que el pedido puede ser confirmado
    if not order.can_be_received_by_buyer():
        messages.error(request, 'Este pedido no puede ser confirmado en su estado actual.')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        receipt_form = OrderConfirmReceiptForm(request.POST)
        rating_form = RatingForm(request.POST)
        
        if receipt_form.is_valid() and rating_form.is_valid():
            # Confirmar recepción
            order.estado = 'completado'
            order.fecha_recepcion = timezone.now()
            
            # Agregar notas de recepción si las hay
            notas_recepcion = receipt_form.cleaned_data.get('notas_recepcion')
            if notas_recepcion:
                if order.notas_comprador:
                    order.notas_comprador += f"\n\nNotas de recepción: {notas_recepcion}"
                else:
                    order.notas_comprador = f"Notas de recepción: {notas_recepcion}"
            
            order.save()
            # Notificar al vendedor que el comprador confirmó recepción y calificó
            create_notification(
                recipient=order.vendedor,
                title='Pedido completado',
                message=f'El comprador confirmó la recepción y calificó el pedido #{order.id}.',
                category='order',
                order_id=order.id,
            )
            
            # Crear calificación
            rating = rating_form.save(commit=False)
            rating.pedido = order
            rating.calificador = request.user
            rating.calificado = order.vendedor
            rating.tipo = 'comprador_a_vendedor'
            rating.save()
            
            messages.success(request, '¡Pedido confirmado y calificación enviada exitosamente!')
            return redirect('order_detail', order_id=order.id)
    else:
        receipt_form = OrderConfirmReceiptForm()
        rating_form = RatingForm()
    
    context = {
        'receipt_form': receipt_form,
        'rating_form': rating_form,
        'order': order
    }
    return render(request, 'sales/confirm_receipt.html', context)


@login_required
def rate_seller_view(request, order_id):
    """Vista para que el comprador califique/edite calificación al vendedor (desde modal)"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Verificar que el usuario es el comprador
    if request.user != order.comprador:
        messages.error(request, 'No tienes permisos para calificar este pedido.')
        return redirect('order_detail', order_id=order.id)
    
    # Verificar que el pedido está completado
    if order.estado != 'completado':
        messages.error(request, 'El pedido debe estar completado para poder calificar.')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        # Buscar si ya existe una calificación
        existing_rating = order.calificaciones.filter(
            calificador=request.user,
            tipo='comprador_a_vendedor'
        ).first()
        
        if existing_rating:
            # Editar calificación existente
            rating = existing_rating
            action_text = 'actualizada'
        else:
            # Crear nueva calificación
            rating = Rating()
            rating.pedido = order
            rating.calificador = request.user
            rating.calificado = order.vendedor
            rating.tipo = 'comprador_a_vendedor'
            action_text = 'enviada'
        
        # Actualizar campos
        rating.calificacion_general = int(request.POST.get('calificacion_general', 0))
        rating.calificacion_comunicacion = int(request.POST.get('calificacion_comunicacion', 0))
        rating.calificacion_puntualidad = int(request.POST.get('calificacion_puntualidad', 0))
        rating.calificacion_calidad = int(request.POST.get('calificacion_calidad', 0))
        rating.comentario = request.POST.get('comentario', '')
        rating.recomendaria = request.POST.get('recomendaria') == 'true'
        rating.save()
        
        messages.success(request, f'¡Calificación {action_text} exitosamente!')
        return redirect('order_detail', order_id=order.id)
    
    # Si no es POST, redirigir al detalle del pedido
    return redirect('order_detail', order_id=order.id)


@login_required
def rate_buyer_view(request, order_id):
    """Vista para que el vendedor califique/edite calificación al comprador (desde modal)"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Verificar que el usuario es el vendedor
    if request.user != order.vendedor:
        messages.error(request, 'No tienes permisos para calificar este pedido.')
        return redirect('order_detail', order_id=order.id)
    
    # Verificar que el pedido está completado
    if order.estado != 'completado':
        messages.error(request, 'El pedido debe estar completado para poder calificar.')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        # Buscar si ya existe una calificación
        existing_rating = order.calificaciones.filter(
            calificador=request.user,
            tipo='vendedor_a_comprador'
        ).first()
        
        if existing_rating:
            # Editar calificación existente
            rating = existing_rating
            action_text = 'actualizada'
        else:
            # Crear nueva calificación
            rating = Rating()
            rating.pedido = order
            rating.calificador = request.user
            rating.calificado = order.comprador
            rating.tipo = 'vendedor_a_comprador'
            action_text = 'enviada'
        
        # Actualizar campos
        rating.calificacion_general = int(request.POST.get('calificacion_general', 0))
        rating.calificacion_comunicacion = int(request.POST.get('calificacion_comunicacion', 0))
        rating.calificacion_puntualidad = int(request.POST.get('calificacion_puntualidad', 0))
        rating.calificacion_calidad = int(request.POST.get('calificacion_calidad', 0))
        rating.comentario = request.POST.get('comentario', '')
        rating.recomendaria = request.POST.get('recomendaria') == 'true'
        rating.save()
        
        messages.success(request, f'¡Calificación {action_text} exitosamente!')
        return redirect('order_detail', order_id=order.id)
    
    # Si no es POST, redirigir al detalle del pedido
    return redirect('order_detail', order_id=order.id)


@login_required
def start_or_go_to_conversation(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    producer = publication.cultivo.productor
    
    # Prevenir que un productor inicie una conversación consigo mismo
    if request.user == producer:
        return redirect('publication_detail', publication_id=publication.id)

    conversation = Conversation.objects.filter(
        publication=publication,
        participants=request.user
    ).filter(
        participants=producer
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(publication=publication)
        conversation.participants.add(request.user, producer)

    return redirect('conversation_detail', conversation_id=conversation.id)

@login_required
def conversation_list(request):
    conversations = request.user.conversations.all().order_by('-updated_at')
    context = {
        'conversations': conversations
    }
    
    # Render different template based on user role to keep appropriate sidebar
    if request.user.role == 'Productor':
        return render(request, 'sales/conversation_list_producer.html', context)
    else:
        return render(request, 'sales/conversation_list_buyer.html', context)


@login_required
def conversations_list_api(request):
    """JSON con últimas conversaciones del usuario para mini chat en el asistente."""
    if request.method != 'GET':
        return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

    from datetime import timedelta
    cutoff = timezone.now() - timedelta(days=15)
    conversations = (
        request.user.conversations
        .filter(updated_at__gte=cutoff)
        .prefetch_related('participants', 'messages__sender')
        .order_by('-updated_at')[:20]
    )

    def other(uqs):
        for u in uqs:
            if u.id != request.user.id:
                return u
        return request.user

    data = []
    for c in conversations:
        last_msg = c.messages.last()
        ou = other(c.participants.all())
        data.append({
            'id': c.id,
            'other_user': ou.get_full_name() or ou.username,
            'last_message': (last_msg.content if last_msg else ''),
            'updated_at': (c.updated_at.isoformat() if hasattr(c, 'updated_at') and c.updated_at else ''),
        })

    archived_count = request.user.conversations.filter(updated_at__lt=cutoff).count()
    return JsonResponse({'success': True, 'conversations': data, 'archived_count': archived_count})

# FUNCIÓN COMENTADA - No tiene template 'sales/conversation_detail.html' y no se usa (se reemplazó por conversation_detail_simple)
# @login_required
@login_required
def conversation_detail_simple(request, conversation_id):
    """Vista simple con polling - NO necesita WebSockets ni Redis"""
    conversation = get_object_or_404(Conversation.objects.prefetch_related('messages__sender'), pk=conversation_id)
    
    # Asegurarse que el usuario es parte de la conversación
    if request.user not in conversation.participants.all():
        return redirect('conversation_list')

    if request.method == 'POST':
        form = MessageForm(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.conversation = conversation
            message.sender = request.user
            message.save()
            
            # Si es una petición AJAX, devolver JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                from django.http import JsonResponse
                return JsonResponse({
                    'success': True,
                    'message': {
                        'id': message.id,
                        'sender_id': message.sender.id,
                        'sender_name': message.sender.get_full_name() or message.sender.username,
                        'content': message.content,
                        'created_at': message.created_at.isoformat(),
                    },
                    'archived': False
                })
            
            return redirect('conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()

    context = {
        'conversation': conversation,
        'form': form
    }
    
    # Render different template based on user role to keep appropriate sidebar
    if request.user.role == 'Productor':
        return render(request, 'sales/conversation_detail_simple_producer.html', context)
    else:
        return render(request, 'sales/conversation_detail_simple_buyer.html', context)


@login_required
def get_new_messages(request, conversation_id):
    """API endpoint para obtener nuevos mensajes (polling)"""
    conversation = get_object_or_404(Conversation, pk=conversation_id)
    
    # Verificar que el usuario es parte de la conversación
    if request.user not in conversation.participants.all():
        from django.http import JsonResponse
        return JsonResponse({'error': 'No autorizado'}, status=403)
    
    since_id = request.GET.get('since', 0)
    try:
        since_id = int(since_id)
    except ValueError:
        since_id = 0
    
    # Obtener mensajes nuevos
    new_messages = conversation.messages.filter(id__gt=since_id).order_by('created_at')
    
    messages_data = []
    for message in new_messages:
        messages_data.append({
            'id': message.id,
            'sender_id': message.sender.id,
            'sender_name': message.sender.get_full_name() or message.sender.username,
            'content': message.content,
            'created_at': message.created_at.isoformat(),
        })
    
    from django.http import JsonResponse
    return JsonResponse({
        'messages': messages_data,
        'count': len(messages_data)
    })

@login_required
def buyer_dashboard(request):
    """Dashboard mejorado para compradores"""
    if request.user.role != 'Comprador':
        messages.error(request, 'Acceso denegado. Solo para compradores.')
        return redirect('index')
    
    # Obtener o crear perfil de comprador
    profile, created = BuyerProfile.objects.get_or_create(user=request.user)
    
    # Estadísticas del comprador
    total_orders = request.user.pedidos_como_comprador.count()
    pending_orders = request.user.pedidos_como_comprador.filter(estado__in=['pendiente', 'confirmado', 'en_preparacion']).count()
    completed_orders = request.user.pedidos_como_comprador.filter(estado='completado').count()
    orders_to_receive = request.user.pedidos_como_comprador.filter(estado__in=['enviado', 'en_transito', 'entregado']).count()
    
    total_spent = request.user.pedidos_como_comprador.filter(
        estado='completado'
    ).aggregate(total=Sum('precio_total'))['total'] or 0
    
    # Pedidos recientes
    recent_orders = request.user.pedidos_como_comprador.select_related(
        'publicacion__cultivo', 'publicacion__cultivo__productor'
    ).order_by('-created_at')[:5]
    
    # Conversaciones activas
    active_conversations = request.user.conversations.select_related('publication').order_by('-updated_at')[:5]
    
    # Calificaciones pendientes
    orders_to_rate = request.user.pedidos_como_comprador.filter(
        estado='completado'
    ).exclude(
        calificaciones__calificador=request.user,
        calificaciones__tipo='comprador_a_vendedor'
    ).count()
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'orders_to_receive': orders_to_receive,
        'orders_to_rate': orders_to_rate,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'active_conversations': active_conversations,
        'profile': profile,
        'recent_notifications': Notification.objects.filter(recipient=request.user).order_by('-created_at')[:10],
    }
    return render(request, 'sales/buyer_dashboard.html', context)


@login_required
def user_profile_view(request, user_id):
    """Vista del perfil público de un usuario con sus calificaciones"""
    from accounts.models import User
    
    user = get_object_or_404(User, pk=user_id)
    
    if user.role == 'Productor':
        profile, created = ProducerProfile.objects.get_or_create(user=user)
    elif user.role == 'Comprador':
        profile, created = BuyerProfile.objects.get_or_create(user=user)
    else:
        profile = None

    # Obtener calificaciones recientes
    recent_ratings_received = Rating.objects.filter(
        calificado=user
    ).select_related('calificador', 'pedido').order_by('-created_at')[:10]
    
    # Estadísticas de calificaciones
    ratings_stats = Rating.objects.filter(calificado=user).aggregate(
        total_ratings=Count('id'),
        avg_general=Avg('calificacion_general'),
        avg_comunicacion=Avg('calificacion_comunicacion'),
        avg_puntualidad=Avg('calificacion_puntualidad'),
        avg_calidad=Avg('calificacion_calidad')
    )
    
    context = {
        'profile_user': user,
        'profile': profile,
        'recent_ratings': recent_ratings_received,
        'ratings_stats': ratings_stats,
        'is_own_profile': request.user == user
    }
    return render(request, 'sales/user_profile.html', context)


@login_required
def cancel_order_view(request, order_id):
    """Vista para cancelar un pedido"""
    order = get_object_or_404(Order, pk=order_id)
    
    # Verificar que el usuario tenga permisos para cancelar
    if not (request.user == order.comprador or request.user == order.vendedor):
        messages.error(request, 'No tienes permisos para cancelar este pedido.')
        return redirect('order_detail', order_id=order.id)
    
    # Verificar que el pedido se pueda cancelar
    if order.estado in ['completado', 'cancelado', 'recibido']:
        messages.error(request, 'Este pedido no se puede cancelar en su estado actual.')
        return redirect('order_detail', order_id=order.id)
    
    if request.method == 'POST':
        # Restaurar la cantidad disponible en la publicación
        publication = order.publicacion
        publication.cantidad_disponible += order.cantidad_acordada
        publication.save()
        
        # Marcar el pedido como cancelado
        order.estado = 'cancelado'
        order.save()
        
        # Determinar quién canceló
        canceller_role = "vendedor" if request.user == order.vendedor else "comprador"
        messages.success(request, f'Pedido cancelado exitosamente por el {canceller_role}. La cantidad ha sido restaurada.')
        
        return redirect('order_detail', order_id=order.id)
    
    context = {
        'order': order,
        'user_role': 'vendedor' if request.user == order.vendedor else 'comprador'
    }
    
    # Render different template based on user role to keep appropriate sidebar
    if request.user.role == 'Productor':
        return render(request, 'sales/cancel_order_producer.html', context)
    else:
        return render(request, 'sales/cancel_order_buyer.html', context)


@login_required
def rankings_view(request):
    """Vista de rankings de usuarios"""
    # Top vendedores
    top_sellers = ProducerProfile.objects.filter(
        user__role='Productor',
        total_ventas__gt=0
    ).select_related('user').order_by(
        '-calificacion_promedio',
        '-total_ventas'
    )[:10]
    
    # Top compradores
    top_buyers = BuyerProfile.objects.filter(
        user__role='Comprador',
        total_compras__gt=0
    ).select_related('user').order_by(
        '-gastos_totales', # Ordenar por gastos puede ser más relevante
        '-total_compras'
    )[:10]
    
    # Vendedores más activos
    most_active_sellers = ProducerProfile.objects.filter(
        user__role='Productor'
    ).select_related('user').order_by('-total_ventas')[:10]
    
    context = {
        'top_sellers': top_sellers,
        'top_buyers': top_buyers,
        'most_active_sellers': most_active_sellers,
    }
    return render(request, 'sales/rankings.html', context)

@login_required
@require_POST
def create_order_from_cart(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = cart.items.all()

    if not cart_items:
        messages.error(request, "Tu carrito está vacío.")
        return redirect('cart:cart_detail')

    created_orders = []
    
    for item in cart_items:
        publication = item.publication

        # Verificar disponibilidad considerando conversión
        disponible, cantidad_disponible = publication.verificar_disponibilidad(float(item.quantity), item.unidad_compra)
        if not disponible:
            disponible_display = cantidad_disponible if cantidad_disponible is not None else publication.cantidad_disponible
            messages.error(
                request,
                f"❌ {publication.cultivo.nombre}: disponible {float(disponible_display):.1f} {item.unidad_compra}"
            )
            return redirect('cart:cart_detail')

        # Convertir la cantidad del carrito a la unidad del vendedor para guardar y descontar stock
        cantidad_en_unidad_vendedor = publication.convertir_unidad(
            float(item.quantity),
            item.unidad_compra,
            publication.unidad_medida,
        )
        if cantidad_en_unidad_vendedor is None:
            messages.error(request, f"❌ {publication.cultivo.nombre}: unidad no convertible")
            return redirect('cart:cart_detail')

        order = Order.objects.create(
            publicacion=publication,
            comprador=request.user,
            cantidad_acordada=round(float(cantidad_en_unidad_vendedor), 2),
            precio_total=item.get_item_price,
            estado='pendiente'
        )
        publication.cantidad_disponible = float(publication.cantidad_disponible) - float(cantidad_en_unidad_vendedor)
        publication.save()
        created_orders.append(order)
        # Notificar al vendedor sobre pedidos creados desde carrito
        create_notification(
            recipient=publication.cultivo.productor,
            title='Nuevo pedido recibido',
            message=f'Pedido #{order.id} creado por {request.user.first_name} desde el carrito.',
            category='order',
            order_id=order.id,
        )

    cart_items.delete()
    
    # Guardar los IDs de los pedidos en la sesión para mostrarlos
    request.session['pending_payment_orders'] = [order.id for order in created_orders]
    
    messages.success(request, f"Se han creado {len(created_orders)} pedido(s) exitosamente. Ahora puedes proceder con el pago.")
    return redirect('cart_checkout_summary')


@login_required
def cart_checkout_summary(request):
    """Vista de resumen después de crear pedidos desde el carrito"""
    from django.conf import settings
    from payments.mercadopago_service import MercadoPagoService
    from payments.models import Payment
    
    order_ids = request.session.get('pending_payment_orders', [])
    
    logger.info("Cart checkout process started")
    logger.info(f"Order IDs from session: {order_ids}")
    logger.info(f"User: {request.user}")
    
    if not order_ids:
        messages.info(request, 'No hay pedidos pendientes de pago.')
        return redirect('order_history')
    
    orders = Order.objects.filter(
        id__in=order_ids,
        comprador=request.user,
        estado='pendiente'
    ).select_related('publicacion__cultivo__productor')
    
    # Calcular total y resumen por unidad de medida
    total = sum(order.precio_total for order in orders)
    totals_by_unit = {}
    for order in orders:
        unit = order.publicacion.unidad_medida
        totals_by_unit[unit] = totals_by_unit.get(unit, 0.0) + float(order.cantidad_acordada)
    totals_by_unit_items = sorted(((u, round(q, 1)) for u, q in totals_by_unit.items()), key=lambda x: x[0])
    
    # Crear datos de checkout para cada pedido
    mercadopago_service = MercadoPagoService()
    orders_with_checkout = []
    
    for order in orders:
        # Crear o obtener pago
        payment, created = Payment.objects.get_or_create(
            order=order,
            user=request.user,
            defaults={
                'amount': order.precio_total,
                'currency': 'COP',
                'payment_method': 'pse',
                'description': f"Pago orden #{order.id}",
                'status': 'pending'
            }
        )
        
        # Crear preferencia de MercadoPago
        preference_result = mercadopago_service.create_preference(order, request.user)
        
        logger.info("Preference result received")
        logger.info(f"Order ID: {order.id}")
        logger.info(f"Success: {preference_result.get('success', False)}")
        logger.info(f"Error: {preference_result.get('error', 'No error')}")
        
        if preference_result['success']:
            payment.mercadopago_id = preference_result['preference_id']
            payment.preference_id = preference_result['preference_id']
            payment.external_reference = preference_result['reference']
            payment.save()
            
            orders_with_checkout.append({
                'order': order,
                'payment': payment,
                'preference_data': preference_result
            })
        else:
            # Agregar el pedido aunque falle la preferencia para mostrar el error
            orders_with_checkout.append({
                'order': order,
                'payment': payment,
                'preference_data': preference_result,
                'error': preference_result.get('error', 'Error desconocido')
            })
    
    # Limpiar sesión después de obtener los pedidos
    if 'pending_payment_orders' in request.session:
        del request.session['pending_payment_orders']
    
    # Seleccionar template base según rol del usuario (sin cambiar el rol)
    # Un vendedor también puede comprar, así que debe usar su template base
    if request.user.role == 'Productor':
        template = 'sales/cart_checkout_summary_producer.html'
    else:
        template = 'sales/cart_checkout_summary.html'
    
    context = {
        'orders_with_checkout': orders_with_checkout,
        'total': total,
        'totals_by_unit_items': totals_by_unit_items,
    }
    return render(request, template, context)
