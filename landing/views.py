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
from .forms import CheckoutForm, OrderDetailsForm, OrderFilesForm
from django.contrib.auth.mixins import LoginRequiredMixin
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

        d_form = OrderDetailsForm()
        f_form = OrderFilesForm()
        context = {
            "title": "cart",
            'order': order,
            'd_form': d_form,
            'f_form': f_form
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

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST)
        if form.is_valid():
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
            cd = form.cleaned_data
            client.name = cd['name']
            client.email = cd['email']
            client.phone = cd['phone']
            client.verified = True
            client.save()
            order.complete = True
            order.save()
            messages.success(self.request, "Ваш заказ принят. Ожидайте звонка от специалиста")
            return redirect('/')

        else:
            messages.error(self.request, "Введите корректные данные")
            return redirect('/checkout/')


from django.core.mail import send_mail
class TestView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        send_mail(
            "Subject",
            "Message",
            "order@nvsnab.com",
            ["mopnerzad@yandex.ru"]
        )
        print()
        print()
        print()
        print(self.request.GET)
        print(self.request.POST)
        print()
        print()
        print()
        context = {
            's_form': SearchForm()
        }
        return render(self.request, "landing/test.html", context)


