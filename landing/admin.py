from django.contrib import admin
from .models import Partner, Order, OrderItem

admin.site.register(Partner)
admin.site.register(Order)
admin.site.register(OrderItem)
