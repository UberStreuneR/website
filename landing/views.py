from functools import reduce

from django.shortcuts import render, redirect
from django.views.generic import View
from .models import Partner, Order
from items.models import Item
from django.db.models import Q
from clients.models import Client
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.templatetags.static import static
from items.forms import SearchForm, HowMuchCounterForm
from .forms import CheckoutForm
# Create your views here.


class HomeView(View):
    def get(self, *args, **kwargs):
        context = {
            "title": "home"
        }
        return render(self.request, "landing/home.html", context=context)


class PriceListsView(View):
    def get(self, *args, **kwargs):
        context = {
            "title": "pricelist"
        }
        return render(self.request, "landing/prices.html", context=context)


class TrademarksView(View):
    def get(self, *args, **kwargs):
        partners = Partner.objects.all()
        context = {
            "title": "trademarks",
            'partners': partners
        }
        return render(self.request, "landing/trademarks.html", context=context)


class AboutView(View):
    def get(self, *args, **kwargs):
        context = {
            "title": "about"
        }
        return render(self.request, "landing/about.html", context=context)


class ContactsView(View):
    def get(self, *args, **kwargs):
        context = {
            "title": "contacts"
        }
        return render(self.request, "landing/contacts.html", context=context)


class CartView(View):
    def get(self, *args, **kwargs):
        try:
            client = self.request.user.client
        except:
            device = self.request.COOKIES['device']
            client, created = Client.objects.get_or_create(device=device)
        try:
            order = Order.objects.get(client=client, complete=False)
        except ObjectDoesNotExist:
            messages.error(self.request, "Добавь сначала что-нибудь в корзину")
            return redirect('/')
        if order.items.count() == 0:
            messages.error(self.request, "Добавь сначала что-нибудь в корзину")
            return redirect('/')
        context = {
            "title": "cart",
            'order': order
        }
        return render(self.request, "landing/cart.html", context=context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()

        try:
            client = self.request.user.client
        except:
            device = self.request.COOKIES['device']
            client, created = Client.objects.get_or_create(device=device)
        try:
            order = Order.objects.get(client=client, complete=False)
        except ObjectDoesNotExist:
            messages.error(self.request, "Добавь сначала что-нибудь в корзину")
            return redirect('/')
        if order.items.count() == 0:
            messages.error(self.request, "Добавь сначала что-нибудь в корзину")
            return redirect('/')
        context = {
            'form': form,
            'order': order
        }
        return render(self.request, "landing/checkout.html", context)



class TestView(View):
    def get(self, *args, **kwargs):
        form = HowMuchCounterForm()
        context = {
            'form': form
        }
        return render(self.request, "landing/test.html", context)
    def post(self, *args, **kwargs):
        form = HowMuchCounterForm(self.request.POST)
        if form.is_valid():
            print(form.cleaned_data)
        else:
            print("None")
        print(self.request.POST)
        print(self.request.GET)
        return redirect("/test")

