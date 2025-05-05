from django import template

register = template.Library()

@register.filter
def abreviar_dia_semana(value):
    if value:
        return value.replace('-feira', '').strip()
    return value
