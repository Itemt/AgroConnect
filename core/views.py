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
    # Rate limit removido - sin restricciones de tiempo
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
                "Eres un asistente de IA experto y profesional de AgroConnect. Responde de manera completa, detallada y técnica. "
                "Para agricultura: incluye datos específicos, técnicas avanzadas, fechas, cantidades, y recomendaciones profesionales. "
                "Para la plataforma: explica procesos paso a paso, soluciona problemas técnicos, da tips avanzados. "
                "Para preguntas generales: responde con información completa, ejemplos prácticos y contexto relevante. "
                "Formato: 3-6 párrafos detallados, usa **negritas** para conceptos clave, listas con '- ' para pasos, y ejemplos concretos. "
                "Incluye datos específicos, fechas, cantidades, técnicas cuando sea relevante. "
                "Termina con una pregunta que profundice en el tema o abra nuevas posibilidades."
            )
            prompt = f"{system_prompt}\n\nPregunta: {raw_message}\n\nResponde de manera detallada y específica:"
            # Respuestas optimizadas para exposición: balance entre calidad y eficiencia
            result = model.generate_content(prompt, generation_config={
                'max_output_tokens': 800,
                'temperature': 0.8,
                'top_k': 45,
                'top_p': 0.9,
            })
            text = (getattr(result, 'text', None) or getattr(result, 'candidates', [None])[0].content.parts[0].text)
            if text:
                response_text = text.strip()
                used_model = 'gemini-1.5-flash'
        except Exception as e:
            # Log del error para diagnóstico
            print(f"Error en Gemini API: {e}")
            # Continuar a fallback silenciosamente
            pass

    # Sistema de respuestas inteligentes cuando no hay API
    if response_text is None:
        # Respuestas contextuales y útiles
        if any(word in user_message for word in ["aplicacion", "app", "agroconnect", "plataforma"]):
            response_text = "**AgroConnect** es una plataforma innovadora que conecta productores agrícolas directamente con compradores, eliminando intermediarios y facilitando el comercio justo. \n\n**Características principales:**\n- Marketplace para productos agrícolas\n- Sistema de pagos seguro con MercadoPago\n- Chat directo entre productores y compradores\n- Gestión de pedidos y seguimiento\n- Dashboard para métricas de ventas\n\n¿Te gustaría conocer más sobre alguna funcionalidad específica?"
        
        elif any(word in user_message for word in ["papas", "papa", "solanum"]):
            response_text = "**Cultivo de Papas** - Guía completa:\n\n**Preparación del suelo:** pH 5.5-6.5, suelo suelto y bien drenado\n**Época de siembra:** En Colombia, marzo-abril y septiembre-octubre\n**Distancia:** Surcos a 30cm, plantas a 25cm\n**Riego:** Moderado, evitar encharcamientos\n**Cosecha:** 3-4 meses después de la siembra\n\n**Variedades recomendadas:** Diacol Capiro, Parda Pastusa, Criolla Colombia\n\n¿Necesitas información sobre alguna etapa específica del cultivo?"
        
        elif any(word in user_message for word in ["tomate", "tomates", "lycopersicon"]):
            response_text = "**Cultivo de Tomates** - Información técnica:\n\n**Clima:** Temperatura óptima 20-25°C\n**Suelo:** Rico en materia orgánica, pH 6.0-6.8\n**Siembra:** En semillero, trasplante a 40-50 días\n**Tutorado:** Necesario para variedades indeterminadas\n**Riego:** Regular, evitar mojar las hojas\n\n**Plagas comunes:** Mosca blanca, trips, nematodos\n**Enfermedades:** Mildiu, oídio, alternaria\n\n¿Quieres saber sobre manejo de plagas o fertilización?"
        
        elif any(word in user_message for word in ["maiz", "maíz", "zea"]):
            response_text = "**Cultivo de Maíz** - Guía técnica:\n\n**Época de siembra:** Abril-mayo y octubre-noviembre\n**Densidad:** 60,000-70,000 plantas/hectárea\n**Fertilización:** NPK 120-60-60 kg/ha\n**Riego:** Crítico en floración y llenado\n**Cosecha:** 4-5 meses, humedad 14-16%\n\n**Variedades:** ICA V-109, ICA V-156, Híbridos\n**Manejo:** Control de malezas, tutorado si es necesario\n\n¿Necesitas información sobre fertilización o control de plagas?"
        
        elif any(word in user_message for word in ["venta", "vender", "comercializar", "precio"]):
            response_text = "**Comercialización en AgroConnect:**\n\n**Para vender:**\n- Regístrate como productor\n- Crea tu perfil y fincas\n- Publica tus productos con precios\n- Gestiona pedidos desde tu dashboard\n\n**Para comprar:**\n- Explora el marketplace\n- Filtra por ubicación y productos\n- Contacta directamente al productor\n- Paga de forma segura\n\n**Ventajas:** Sin intermediarios, precios justos, comunicación directa\n\n¿Eres productor o comprador? Te puedo ayudar con el proceso específico."
        
        elif any(word in user_message for word in ["pago", "pagar", "mercadopago", "dinero"]):
            response_text = "**Sistema de Pagos en AgroConnect:**\n\n**Métodos aceptados:**\n- Tarjetas de crédito y débito\n- Transferencias bancarias\n- Pago en efectivo (coordinado)\n\n**Proceso seguro:**\n- Pagos procesados por MercadoPago\n- Fondos liberados al confirmar recepción\n- Protección para compradores y vendedores\n\n**Ventajas:**\n- Transacciones seguras\n- Sin comisiones ocultas\n- Respaldo de MercadoPago\n\n¿Tienes alguna duda específica sobre pagos?"
        
        elif any(word in user_message for word in ["ayuda", "help", "soporte", "problema"]):
            response_text = "**Centro de Ayuda AgroConnect:**\n\n**Funcionalidades principales:**\n- Marketplace de productos agrícolas\n- Sistema de mensajería directa\n- Gestión de pedidos y pagos\n- Dashboard de métricas\n\n**Soporte técnico:**\n- Chat en tiempo real\n- Documentación completa\n- Tutoriales paso a paso\n\n**Contacto:**\n- Email: contacto@agroconnect.com\n- Teléfono: +57 300 123 4567\n\n¿En qué específicamente necesitas ayuda?"
        
        else:
            response_text = "**¡Hola! Soy el asistente de AgroConnect** 🌱\n\nPuedo ayudarte con:\n- **Información sobre cultivos** (papas, tomates, maíz, etc.)\n- **Uso de la plataforma** (vender, comprar, pagos)\n- **Técnicas agrícolas** (siembra, riego, fertilización)\n- **Soporte técnico** (problemas, dudas)\n\n**¿Sobre qué te gustaría saber?** Puedes preguntarme sobre cultivos, la plataforma, o cualquier tema agrícola."
        
        used_model = 'agroconnect-assistant'

    # Rate limit removido - no se guarda timestamp
    return JsonResponse({"success": True, "reply": response_text, "model": used_model})


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
            model = genai.GenerativeModel('gemini-1.5-flash')
            
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
            
            result = model.generate_content(prompt, generation_config={
                'max_output_tokens': 400,
                'temperature': 0.7,
                'top_k': 40,
                'top_p': 0.9,
            })
            
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
    
    # Guardar timestamp
    request.session['ai_suggestions_last_ts'] = str(now_ts)
    
    return JsonResponse({
        'success': True, 
        'suggestions': suggestions, 
        'model': used_model
    })