from django.db import models
from django.contrib.auth.models import User
from clients.models import Client
from items.models import Item
from django.utils import timezone


class Partner(models.Model):
    name = models.CharField(max_length=50)
    image = models.ImageField()
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name}, partner"


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        return self.quantity * self.item.price


class Order(models.Model):
    client = models.ForeignKey(Client, related_name="orders", on_delete=models.CASCADE, blank=True)
    date = models.DateTimeField(default=timezone.now)
    items = models.ManyToManyField(OrderItem, blank=True)
    price = models.IntegerField(default=0)
    complete = models.BooleanField(default=False)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total
