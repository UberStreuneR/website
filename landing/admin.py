from django.contrib import admin
from .models import Partner, Order, OrderItem, File

admin.site.register(Partner)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(File)
