from django import template
register = template.Library()

@register.filter
def truncate_name(name):
    return name[1:-1]