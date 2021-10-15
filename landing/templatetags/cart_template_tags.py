from django import template
from landing.models import Order
from clients.models import Client
register = template.Library()


@register.filter
def cart_item_count(request):
    try:
        client = request.user.client
    except:
        device = request.COOKIES['device']
        client, created = Client.objects.get_or_create(device=device)
    user = request.user
    if user.is_authenticated:
        qs = Order.objects.filter(client=client, complete=False)
        if qs.exists():
            return qs[0].items.count()
    return 0