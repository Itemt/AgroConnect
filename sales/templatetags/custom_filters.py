from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
def get_other_user(participants, current_user):
    return participants.exclude(id=current_user.id).first()

@register.simple_tag
def render_stars(rating, size='xs'):
    """Renderiza estrellas visuales basadas en una calificación (0-5)"""
    try:
        rating_value = float(rating) if rating else 0.0
    except (ValueError, TypeError):
        rating_value = 0.0
    
    stars_html = []
    for i in range(1, 6):
        if rating_value >= i:
            stars_html.append(f'<i class="fas fa-star text-yellow-500 text-{size}"></i>')
        elif rating_value >= i - 0.5:
            stars_html.append(f'<i class="fas fa-star-half-alt text-yellow-500 text-{size}"></i>')
        else:
            stars_html.append(f'<i class="far fa-star text-yellow-500 text-{size} opacity-40"></i>')
    
    return mark_safe(''.join(stars_html))
