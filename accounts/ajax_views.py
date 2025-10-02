from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.colombia_locations import COLOMBIA_LOCATIONS


@require_http_methods(["GET"])
def get_cities_by_department(request):
    """Vista AJAX para obtener ciudades por departamento"""
    department = request.GET.get('department', '')
    
    if department in COLOMBIA_LOCATIONS:
        cities = sorted(COLOMBIA_LOCATIONS[department])
        return JsonResponse({'success': True, 'cities': cities})
    
    return JsonResponse({'success': False, 'cities': []})
