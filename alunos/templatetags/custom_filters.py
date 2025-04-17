# alunos/templatetags/custom_filters.py

from django import template
import re
from datetime import date

register = template.Library()

@register.filter
def get_item(dictionary, key):
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None

@register.filter
def to(value, arg):
    try:
        return range(int(value), int(arg) + 1)
    except (ValueError, TypeError):
        return []

@register.filter
def regex_sub(value, args):
    try:
        pattern, replacement = args.split(',')
        return re.sub(pattern, replacement, value)
    except Exception:
        return value

@register.filter
def calcular_idade(nascimento):
    if not nascimento:
        return ""
    hoje = date.today()
    return hoje.year - nascimento.year - ((hoje.month, hoje.day) < (nascimento.month, nascimento.day))

@register.filter(name='replace')
def replace(value, args):
    try:
        old, new = args.split(' ')
        return value.replace(old, new)
    except Exception:
        return value

@register.filter
def attr(obj, nome_campo):
    return getattr(obj, nome_campo, '')

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
