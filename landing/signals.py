from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Order
from clients.models import Client
from django.core.exceptions import ObjectDoesNotExist

# @receiver(post_save, sender=Order)
# def create_client(sender, instance, created, **kwargs):
#     if created:
#         try:
#             client = Client.objects.filter(name=kwargs['name'], phone=kwargs['phone']).first()
#         except ObjectDoesNotExist:
#             client = Client.objects.create(name=kwargs['name'], phone=kwargs['phone']).first()
#         instance.client = client
#         instance.save()
#
# @receiver(post_save, sender=Order)
# def save_order(sender, instance, **kwargs):
#     instance.price = instance.get_total()
#     instance.save()