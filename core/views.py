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

@login_required
@require_POST
def notifications_delete_all(request):
    """Eliminar todas las notificaciones del usuario"""
    deleted_count = Notification.objects.filter(recipient=request.user).count()
    Notification.objects.filter(recipient=request.user).delete()
    return JsonResponse({'success': True, 'deleted_count': deleted_count})

@login_required
@require_POST
def notifications_delete_read(request):
    """Eliminar solo las notificaciones leídas del usuario"""
    deleted_count = Notification.objects.filter(recipient=request.user, is_read=True).count()
    Notification.objects.filter(recipient=request.user, is_read=True).delete()
    return JsonResponse({'success': True, 'deleted_count': deleted_count})

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
    """Endpoint para el chatbot con IA"""
    import json
    import os
    
    print(f"=== CHATBOT CALLED ===")
    print(f"Request body: {request.body}")

    try:
        data = json.loads(request.body or '{}')
        print(f"Parsed data: {data}")
    except Exception as e:
        print(f"JSON parse error: {e}")
        data = {}

    raw_message = (data.get('message') or '').strip()
    print(f"Raw message: '{raw_message}'")
    
    if not raw_message:
        return JsonResponse({"success": False, "error": "No message provided"})
    
    # Verificar API key
    api_key = os.getenv('GOOGLE_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
    print(f"API Key found: {bool(api_key)}")
    print(f"API Key (first 10 chars): {api_key[:10] if api_key else 'NOT_SET'}")
    
    if not api_key:
        return JsonResponse({
            "success": True, 
            "reply": "**Configuración requerida** 🔧\n\nPara usar el asistente de IA, necesitas configurar la API key de Gemini en las variables de entorno del servidor.\n\n**Variable requerida:** `GOOGLE_API_KEY`\n\n**Sin la API key, el asistente no puede funcionar.**",
            "model": "config-required"
        })
    
    # Usar Gemini API
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        # Modelo económico y disponible según tu panel
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        system_prompt = (
            "Eres un asistente de IA experto y profesional de AgroConnect. Responde de manera completa, detallada y técnica. "
            "Para agricultura: incluye datos específicos, técnicas avanzadas, fechas, cantidades, y recomendaciones profesionales. "
            "Para la plataforma: explica procesos paso a paso, soluciona problemas técnicos, da tips avanzados. "
            "Para preguntas generales: responde con información completa, ejemplos prácticos y contexto relevante. "
            "Formato: 3-6 párrafos detallados, usa **negritas** para conceptos clave, listas con '- ' para pasos, y ejemplos concretos. "
            "Incluye datos específicos, fechas, cantidades, técnicas cuando sea relevante. "
            "Termina con una pregunta que profundice en el tema o abra nuevas posibilidades."
        )
        
        prompt = f"{system_prompt}\n\nPregunta: {raw_message}\n\nResponde de manera detallada y específica:"
        
        result = model.generate_content(
            prompt,
            generation_config={
                # 600–800 tokens por respuesta, configuramos 700 por defecto
                'max_output_tokens': 700,
                # Temperatura moderada para mantener respuestas enfocadas
                'temperature': 0.6,
                'top_k': 30,
                'top_p': 0.85,
            }
        )
        
        text = (getattr(result, 'text', None) or getattr(result, 'candidates', [None])[0].content.parts[0].text)
        
        if text:
            return JsonResponse({
                "success": True, 
                "reply": text.strip(), 
                "model": "gemini-2.0-flash"
            })
        else:
            return JsonResponse({
                "success": True, 
                "reply": "**Error de procesamiento** ⚠️\n\nNo pude generar una respuesta. Por favor intenta de nuevo.",
                "model": "error"
            })
            
    except Exception as e:
        print(f"Error en Gemini API: {e}")
        return JsonResponse({
            "success": True, 
            "reply": f"**Error de API** ⚠️\n\nError: {str(e)}\n\nPor favor verifica la configuración de la API key.",
            "model": "api-error"
        })



# --- AI Suggestions for Publications ---
@require_POST
def ai_publication_suggestions(request):
    """Genera sugerencias de IA para publicaciones de cultivos"""
    import json
    
    try:
        data = json.loads(request.body or '{}')
    except Exception:
        return JsonResponse({'success': False, 'error': 'Datos inválidos'})
    
    # Obtener datos del cultivo
    crop_name = data.get('crop_name', '').strip()
    crop_category = data.get('crop_category', '').strip()
    crop_quantity = data.get('crop_quantity', 0)
    crop_unit = data.get('crop_unit', '').strip()
    location = data.get('location', '').strip()
    
    if not crop_name:
        return JsonResponse({'success': False, 'error': 'Nombre del cultivo requerido'})
    
    # Rate limit para sugerencias (más permisivo)
    # Rate limit removido - sin restricciones de tiempo para sugerencias
    # Intentar IA para sugerencias
    suggestions = None
    used_model = 'fallback'
    
    # Leer API key
    api_key = (
        config('GOOGLE_API_KEY', default='')
        or config('GEMINI_API_KEY', default='')
    )
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Prompt optimizado para sugerencias de mercado colombiano
            prompt = f"""Eres un experto en mercado agrícola colombiano. Genera sugerencias para una publicación de cultivo.

DATOS DEL CULTIVO:
- Producto: {crop_name}
- Categoría: {crop_category}
- Cantidad: {crop_quantity} {crop_unit}
- Ubicación: {location}

GENERA SUGERENCIAS EN FORMATO JSON:
{{
    "title_suggestions": ["Título 1", "Título 2", "Título 3"],
    "price_suggestions": {{
        "min_price": 0.0,
        "max_price": 0.0,
        "recommended_price": 0.0,
        "reasoning": "Explicación del precio"
    }},
    "description_suggestions": ["Descripción 1", "Descripción 2"],
    "marketing_tips": ["Tip 1", "Tip 2", "Tip 3"]
}}

REGLAS:
- Precios en COP por {crop_unit}
- Basado en mercado colombiano actual
- Títulos atractivos y descriptivos
- Descripciones que resalten calidad y origen
- Tips de marketing específicos para Colombia
- Máximo 3 sugerencias por categoría"""
            
            result = model.generate_content(
                prompt,
                generation_config={
                    'max_output_tokens': 400,
                    'temperature': 0.6,
                    'top_k': 30,
                    'top_p': 0.85,
                }
            )
            
            text = (getattr(result, 'text', None) or getattr(result, 'candidates', [None])[0].content.parts[0].text)
            if text:
                # Intentar parsear JSON
                try:
                    suggestions = json.loads(text.strip())
                    used_model = 'gemini-1.5-flash'
                except:
                    # Si no es JSON válido, usar como texto
                    suggestions = {'raw_response': text.strip()}
                    used_model = 'gemini-1.5-flash'
                    
        except Exception as e:
            print(f"Error en IA para sugerencias: {e}")
            pass
    
    # Fallback si no hay IA
    if suggestions is None:
        suggestions = {
            "title_suggestions": [
                f"{crop_name} fresco de {location}",
                f"{crop_name} de calidad premium",
                f"{crop_name} directo del productor"
            ],
            "price_suggestions": {
                "min_price": 1000.0,
                "max_price": 5000.0,
                "recommended_price": 2500.0,
                "reasoning": "Precio sugerido basado en mercado local"
            },
            "description_suggestions": [
                f"{crop_name} cultivado con técnicas tradicionales",
                f"{crop_name} fresco y de excelente calidad"
            ],
            "marketing_tips": [
                "Destaca la frescura del producto",
                "Menciona el origen local",
                "Incluye fotos de calidad"
            ]
        }
        used_model = 'fallback'
    
    # Rate limit removido - no se guarda timestamp
    
    return JsonResponse({
        'success': True, 
        'suggestions': suggestions, 
        'model': used_model
    })