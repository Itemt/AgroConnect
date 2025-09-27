from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Sum
from .models import Conversation, Message, Order
from marketplace.models import Publication
from .forms import MessageForm, OrderForm

# Create your views here.

@login_required
def create_order_view(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)

    if request.user.role != 'Comprador' or request.user == publication.cultivo.productor:
        # Redirigir si no es un comprador o si es el dueño de la publicación
        return redirect('publication_detail', publication_id=publication.id)

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.publicacion = publication
            order.comprador = request.user
            
            # Calcular precio final
            order.precio_total = order.cantidad_acordada * publication.precio_por_unidad
            order.estado = 'confirmado' # Estado inicial
            
            # Validar que la cantidad no exceda la disponible
            if order.cantidad_acordada > publication.cantidad_disponible:
                form.add_error('cantidad_acordada', 'La cantidad solicitada excede la disponible.')
            else:
                # Actualizar la cantidad disponible en la publicación
                publication.cantidad_disponible -= order.cantidad_acordada
                publication.save()
                
                order.save()
                return redirect('order_history') # Redirigir al historial de pedidos
    else:
        form = OrderForm()

    context = {
        'form': form,
        'publication': publication
    }
    return render(request, 'sales/order_form.html', context)


@login_required
def order_history_view(request):
    if request.user.role == 'Comprador':
        orders = Order.objects.filter(comprador=request.user).order_by('-created_at')
    elif request.user.role == 'Productor':
        orders = Order.objects.filter(publicacion__cultivo__productor=request.user).order_by('-created_at')
    else:
        orders = []

    return render(request, 'sales/order_history.html', {'orders': orders})


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
    return render(request, 'sales/conversation_list.html', context)

@login_required
def conversation_detail(request, conversation_id):
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
            return redirect('conversation_detail', conversation_id=conversation.id)
    else:
        form = MessageForm()

    # Marcar mensajes como leídos (funcionalidad futura)
    # conversation.messages.filter(recipient=request.user, is_read=False).update(is_read=True)

    context = {
        'conversation': conversation,
        'form': form
    }
    return render(request, 'sales/conversation_detail.html', context)

@login_required
def buyer_dashboard(request):
    """Dashboard principal para compradores"""
    if request.user.role != 'Comprador':
        messages.error(request, 'Acceso denegado. Solo para compradores.')
        return redirect('index')
    
    # Estadísticas del comprador
    total_orders = request.user.pedidos_como_comprador.count()
    pending_orders = request.user.pedidos_como_comprador.filter(estado='confirmado').count()
    completed_orders = request.user.pedidos_como_comprador.filter(estado='entregado').count()
    total_spent = request.user.pedidos_como_comprador.filter(
        estado='entregado'
    ).aggregate(total=Sum('precio_total'))['total'] or 0
    
    # Pedidos recientes
    recent_orders = request.user.pedidos_como_comprador.select_related(
        'publicacion__cultivo', 'publicacion__cultivo__productor'
    ).order_by('-created_at')[:5]
    
    # Conversaciones activas
    active_conversations = request.user.conversations.count()
    
    context = {
        'total_orders': total_orders,
        'pending_orders': pending_orders,
        'completed_orders': completed_orders,
        'total_spent': total_spent,
        'recent_orders': recent_orders,
        'active_conversations': active_conversations,
    }
    return render(request, 'sales/buyer_dashboard.html', context)
