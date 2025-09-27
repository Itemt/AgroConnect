from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Conversation, Publication
from .forms import MessageForm

# Create your views here.

@login_required
def start_or_go_to_conversation(request, publication_id):
    publication = get_object_or_404(Publication, pk=publication_id)
    producer = publication.crop.producer
    
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
