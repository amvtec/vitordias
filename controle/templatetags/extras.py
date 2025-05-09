from django import template

register = template.Library()

@register.filter
def get_label(label_list, value):
    for campo, label in label_list:
        if campo == value:
            return label
    return value
