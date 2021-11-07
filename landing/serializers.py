from rest_framework import serializers
from .models import Order, OrderItem
from items.models import Item



class ItemSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='get_absolute_url')
    cool_price = serializers.CharField(source='get_cool_price')
    class Meta:
        model = Item
        fields = '__all__'

class OrderItemSerializer(serializers.ModelSerializer):
    item = ItemSerializer()
    cool_price = serializers.CharField(source='get_cool_price')
    class Meta:
        model = OrderItem
        fields = '__all__'

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    cool_price = serializers.CharField(source='get_cool_price')
    class Meta:
        model = Order
        fields = '__all__'

