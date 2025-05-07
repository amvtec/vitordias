from django import template

register = template.Library()

@register.filter
def abreviar_dia_semana(value):
    if value:
        return value.replace('-feira', '').strip()
    return value

MESES_PT_BR = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}

@register.filter
def mes_extenso(numero_mes):
    return MESES_PT_BR.get(numero_mes, "")

