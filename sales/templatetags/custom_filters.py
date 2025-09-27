from django import template

register = template.Library()

@register.filter
def get_other_user(participants, current_user):
    return participants.exclude(id=current_user.id).first()
