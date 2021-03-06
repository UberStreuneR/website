from django import template
from landing.models import Order
from clients.models import Client
register = template.Library()

@register.filter
def cart_item_count(request):
    try:
        client = request.user.client
    except:
        try:
            device = request.COOKIES['device']
        except KeyError:
            return 0 # Иначе не прогрузится страница, т.к. cookie еще не сгенерирован
        client, created = Client.objects.get_or_create(device=device)

    qs = Order.objects.filter(client=client, complete=False)
    if qs.exists():
        return qs[0].items.count()
    return 0

@register.filter
def cart_items(request):
    try:
        client = request.user.client
    except:
        try:
            device = request.COOKIES['device']
        except KeyError:
            return 0 # Иначе не прогрузится страница, т.к. cookie еще не сгенерирован
        client, created = Client.objects.get_or_create(device=device)

    qs = Order.objects.filter(client=client, complete=False)

    return qs[0].items.all()

@register.filter
def cart_sum(request):
    try:
        client = request.user.client
    except:
        try:
            device = request.COOKIES['device']
        except KeyError:
            return 0 # Иначе не прогрузится страница, т.к. cookie еще не сгенерирован
        client, created = Client.objects.get_or_create(device=device)

    qs = Order.objects.filter(client=client, complete=False)
    if qs.exists():
        order = qs[0]
        return order.get_cool_price()
    else:
        return 0

    return qs[0].items.all()


@register.filter
def no_extension(name):
    return name[:name.find(".")]