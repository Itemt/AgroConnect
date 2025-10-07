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
    # Rate limit simple por sesión: 1 solicitud cada 4s
    last_ts = request.session.get('assistant_last_ts')
    now_ts = timezone.now().timestamp()
    min_interval = 4.0
    if last_ts and (now_ts - float(last_ts)) < min_interval:
        retry_after = max(1, int(min_interval - (now_ts - float(last_ts))))
        return JsonResponse({'success': False, 'error': 'rate_limited', 'retry_after': retry_after}, status=429)
    # Limitar tamaño de entrada para controlar consumo (más estricto)
    if len(raw_message) > 800:
        raw_message = raw_message[:800]
    user_message = raw_message.lower()

    # Intentar SIEMPRE IA primero si hay clave
    used_model = 'fallback'
    response_text = None

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
                "Eres un asistente de IA muy inteligente y detallado. Responde de manera completa, elaborada y profesional. "
                "Sé específico, da ejemplos concretos, incluye datos técnicos cuando sea relevante. "
                "Usa **negritas** para conceptos importantes y listas con '- ' para pasos. "
                "Responde de manera natural y conversacional, como un experto que realmente sabe del tema. "
                "No uses respuestas genéricas - sé específico y útil."
            )
            prompt = f"{system_prompt}\n\nPregunta: {raw_message}\n\nResponde de manera detallada y específica:"
            # Respuestas MUY elaboradas: muchos tokens y alta creatividad
            result = model.generate_content(prompt, generation_config={
                'max_output_tokens': 500,
                'temperature': 0.9,
                'top_k': 50,
                'top_p': 0.95,
            })
            text = (getattr(result, 'text', None) or getattr(result, 'candidates', [None])[0].content.parts[0].text)
            if text:
                response_text = text.strip()
                used_model = 'gemini-1.5-flash'
        except Exception:
            # Continuar a fallback silenciosamente
            pass

    # Sin fallback - solo IA o error
    if response_text is None:
        return JsonResponse({
            'success': False, 
            'error': 'No se pudo generar respuesta. Intenta de nuevo.',
            'used_model': 'none'
        })

    # Guardar timestamp de la solicitud atendida
    request.session['assistant_last_ts'] = str(now_ts)
    return JsonResponse({"success": True, "reply": response_text, "model": used_model})