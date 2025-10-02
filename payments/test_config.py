"""
Vista temporal para verificar la configuración de ePayco
"""
from django.http import JsonResponse
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def check_epayco_config(request):
    """Verificar la configuración de ePayco"""
    config = {
        'public_key_set': bool(settings.EPAYCO_PUBLIC_KEY),
        'public_key_length': len(settings.EPAYCO_PUBLIC_KEY) if settings.EPAYCO_PUBLIC_KEY else 0,
        'private_key_set': bool(settings.EPAYCO_PRIVATE_KEY),
        'test_mode': settings.EPAYCO_TEST_MODE,
        'response_url': settings.EPAYCO_RESPONSE_URL,
        'confirmation_url': settings.EPAYCO_CONFIRMATION_URL,
    }
    
    # Solo mostrar primeros caracteres de las claves por seguridad
    if settings.EPAYCO_PUBLIC_KEY:
        config['public_key_preview'] = settings.EPAYCO_PUBLIC_KEY[:10] + '...'
    
    return JsonResponse(config)

