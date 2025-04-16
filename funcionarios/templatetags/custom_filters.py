from django import template

register = template.Library()

@register.filter
def primeiros_dois_nomes(nome):
    if not nome:
        return ''
    partes = nome.split()
    return ' '.join(partes[:2]) if len(partes) >= 2 else nome

@register.filter
def somar_horas(valor1, valor2):
    try:
        return float(valor1) + float(valor2)
    except (TypeError, ValueError):
        return valor1 or 0
