from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_GET, require_POST
from django.utils import timezone
from django.core.paginator import Paginator
from .models import Notification
from django.shortcuts import render
from decouple import config


@login_required
@require_GET
def notifications_list(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')[:20]
    data = [
        {
            'id': n.id,
            'title': n.title,
            'message': n.message,
            'category': n.category,
            'order_id': n.order_id,
            'payment_id': n.payment_id,
            'created_at': timezone.localtime(n.created_at).isoformat(),
            'is_read': n.is_read,
        }
        for n in notifications
    ]
    return JsonResponse({'success': True, 'notifications': data})


@login_required
@require_POST
def notifications_mark_all_read(request):
    Notification.objects.filter(recipient=request.user, is_read=False).update(is_read=True, read_at=timezone.now())
    return JsonResponse({'success': True})

@login_required
@require_POST
def notifications_mark_all_unread(request):
    Notification.objects.filter(recipient=request.user, is_read=True).update(is_read=False, read_at=None)
    return JsonResponse({'success': True})


@login_required
@require_POST
def notifications_mark_read(request):
    import json
    data = json.loads(request.body)
    notification_id = data.get('notification_id')
    if notification_id:
        Notification.objects.filter(id=notification_id, recipient=request.user).update(is_read=True)
    return JsonResponse({'success': True})

from django.shortcuts import render

# Create your views here.

def index(request):
    return render(request, 'index.html')

@login_required
def notifications_page(request):
    """Vista para mostrar todas las notificaciones del usuario"""
    notifications = Notification.objects.filter(recipient=request.user).order_by('-created_at')
    
    # Paginación
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Estadísticas
    total_notifications = notifications.count()
    unread_count = notifications.filter(is_read=False).count()
    
    context = {
        'page_obj': page_obj,
        'total_notifications': total_notifications,
        'unread_count': unread_count,
    }
    
    return render(request, 'core/notifications.html', context)


# --- Simple AI Assistant endpoint (stub) ---
@require_POST
def assistant_reply(request):
    """Lightweight endpoint that returns an informative response for the assistant bubble.

    For now, it uses simple heuristics to provide guidance about the platform and
    agricultural context without external API calls. Later this can integrate with
    a real LLM provider.
    """
    import json

    try:
        data = json.loads(request.body or '{}')
    except Exception:
        data = {}

    raw_message = (data.get('message') or '').strip()
    # Limitar tamaño de entrada para controlar consumo
    if len(raw_message) > 1200:
        raw_message = raw_message[:1200]
    user_message = raw_message.lower()

    # Very simple intent detection
    response_text = (
        "Hola, soy tu asistente de AgroConnect. Puedo ayudarte con: \n"
        "- Cómo publicar o comprar productos.\n"
        "- Estados de pedidos y pagos.\n"
        "- Conceptos básicos agrícolas (rendimientos, épocas de siembra generales).\n"
        "Cuéntame, ¿en qué te ayudo?"
    )

    if user_message:
        if any(k in user_message for k in ["publicar", "venta", "vender", "anuncio", "producto"]):
            response_text = (
                "Para publicar: ve a tu Dashboard de Productor > Cultivos y crea un nuevo cultivo. "
                "Luego, en Marketplace, publica la oferta indicando precio, cantidad y fotos."
            )
        elif any(k in user_message for k in ["comprar", "pedido", "orden", "carrito"]):
            response_text = (
                "Para comprar: entra al Marketplace, agrega productos al carrito y continúa al pago. "
                "Podrás revisar el estado en tu Dashboard de Comprador."
            )
        elif any(k in user_message for k in ["pago", "epayco", "transaccion", "transacción"]):
            response_text = (
                "Los pagos se procesan con ePayco. Si tu pago aparece pendiente, suele confirmarse en minutos. "
                "Si se cancela, verifica tu método de pago o inténtalo nuevamente."
            )
        elif any(k in user_message for k in ["papa", "maiz", "arroz", "siembra", "cosecha", "clima"]):
            response_text = (
                "Consejo general: Ajusta fechas de siembra y riego según el clima local. "
                "Usa semillas certificadas cuando sea posible y rota cultivos para mejorar el suelo."
            )
        elif any(k in user_message for k in ["contacto", "soporte", "ayuda", "whatsapp", "email"]):
            response_text = (
                "Soporte: contacto@agroconnect.com. Comparte tu problema y el ID del pedido si aplica."
            )

    # Try Gemini if key is configured
    # Leer desde .env/variables de entorno
    api_key = (
        config('GOOGLE_API_KEY', default='')
        or config('GEMINI_API_KEY', default='')
    )
    if api_key and raw_message:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            system_prompt = (
                "Asistente de AgroConnect en español. Responde breve (máx. 6 líneas), claro y práctico. "
                "Temas: uso de la plataforma (publicar, comprar, pagos ePayco, pedidos) y consejos agrícolas generales."
            )
            prompt = f"{system_prompt}\n\nUsuario: {raw_message}\nAsistente (máx. 6 líneas):"
            # Pedimos una respuesta corta y barata
            result = model.generate_content(prompt, generation_config={
                'max_output_tokens': 180,
                'temperature': 0.6,
            })
            text = (getattr(result, 'text', None) or getattr(result, 'candidates', [None])[0].content.parts[0].text)
            if text:
                response_text = text.strip()
        except Exception:
            # Keep heuristic fallback silently
            pass

    return JsonResponse({"success": True, "reply": response_text})