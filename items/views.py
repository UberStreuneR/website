from django.shortcuts import render
from django.views.generic import View
from .models import Item

equivalents = {
    'gas-boilers': 'Газовые котлы',
    'electric-boilers': 'Электрические котлы',
    'pellet-boilers': 'Пеллетные котлы',
    'water-heaters': 'Водонагреватели',
}

class CategoryListView(View):
    def get(self, *args, **kwargs):
        items = Item.objects.filter(category=kwargs['category'].upper())
        context = {
            'items': items
        }
        return render(self.request, "items/categories.html", context)

class ItemList(View):
    def get(self, *args, **kwargs):
        items = Item.objects.filter(category=kwargs['category'].upper(), subcategory=kwargs['subcategory'].upper())
        context = {
            'items': items,
            'name': equivalents[kwargs['subcategory']]
        }
        return render(self.request, "items/subcategories.html", context)
