from django import template

register = template.Library()

@register.filter
def primeiros_dois_nomes(nome):
    if not nome:
        return ''
    partes = nome.split()
    return ' '.join(partes[:2]) if len(partes) >= 2 else nome
