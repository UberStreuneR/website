from django.shortcuts import render
from django.views.generic import View
from .models import Item


class BlueThingsListView(View):
    def get(self, *args, **kwargs):
        items = Item.objects.filter(category="BT")
        context = {
            'items': items
        }
        return render(self.request, "items/blue-things.html", context)

