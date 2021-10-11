from django import template
from landing.models import Order

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(client=user.client, ordered=False)
        if qs.exists():
            return qs[0].commodities.count()
    return 0