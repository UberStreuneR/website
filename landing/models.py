from django.db import models
from django.contrib.auth.models import User
from clients.models import Client
from items.models import Item
from django.utils import timezone


class Partner(models.Model):
    name = models.CharField(max_length=250)
    image = models.ImageField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def save(self, *args, **kwargs):
        name = self.name.lower()
        self.image = f'static/landing/images/mainpage/{name}.jpg'
        super(Partner, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.name}, partner"


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.name}"

    def get_total_item_price(self):
        if self.item.price < 0:
            return 0
        return self.quantity * self.item.price

    def get_cool_price(self):
        if self.item.price == -1:
            return "Цена не установлена"
        if self.item.price == -2:
            return "Цена по запросу"
        price = str(self.get_total_item_price())
        values = price.split(".")
        values[1] = values[1][:2]
        int_price = values[0]
        for i in range(3, len(int_price) + 1, 4):
            int_price = int_price[:-i] + " " + int_price[-i:]
        return int_price


class Order(models.Model):
    client = models.ForeignKey(Client, related_name="orders", on_delete=models.CASCADE, blank=True)
    date = models.DateTimeField(default=timezone.now)
    items = models.ManyToManyField(OrderItem, blank=True)
    price = models.IntegerField(default=0)
    details = models.TextField(blank=True, null=True)

    complete = models.BooleanField(default=False)
    fulfilled = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)

    def get_total(self):
        total = 0
        for order_item in self.items.all():
            total += order_item.get_total_item_price()
        return total

    def get_cool_price(self):
        price = str(self.get_total())
        if not "." in price:
            return price
        else:
            values = price.split(".")
            values[1] = values[1][:2]
            int_price = values[0]
            for i in range(3, len(int_price) + 1, 4):
                int_price = int_price[:-i] + " " + int_price[-i:]
            return int_price

class File(models.Model):
    order = models.ForeignKey(Order, related_name='files', on_delete=models.CASCADE)
    name = models.CharField(blank=True, null=True, max_length=200)
    file = models.FileField(blank=True, null=True, upload_to='static/cart_files/')
