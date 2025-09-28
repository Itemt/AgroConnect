from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from core.colombia_locations import COLOMBIA_LOCATIONS


@require_http_methods(["GET"])
def get_cities_by_department(request):
    """Vista AJAX para obtener ciudades por departamento"""
    department = request.GET.get('department', '')
    
    if department in COLOMBIA_LOCATIONS:
        cities = COLOMBIA_LOCATIONS[department]
        city_choices = [{'value': city, 'text': city} for city in sorted(cities)]
        return JsonResponse({'success': True, 'cities': city_choices})
    
    return JsonResponse({'success': False, 'cities': []})
