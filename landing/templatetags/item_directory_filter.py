from django import template
register = template.Library()


@register.filter
def slash_to_hat_filter(name):
    return name.replace("/", "^")

