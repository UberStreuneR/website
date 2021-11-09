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
from django.core.mail import EmailMessage
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
import os, shutil
import pandas as pd


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

            body = f"Имя: {client.name}" + "\n" + f"Телефон: {client.phone}" + "\n" + f"Почта: {client.email}" + "\n" + f"Детали заказа: {order.details}"
            email = EmailMessage(
                'Order',
                body,
                'order@nvsnab.com',
                ['order@nvsnab.com']
            )
            files = order.files.all()
            for file in files:
                with open(os.path.join(BASE_DIR, file.file.path), "rb") as f:
                    email.attach_file(f.name)
            df = pd.DataFrame()
            for order_item in order.items.all():
                item_series = pd.Series({"Брэнд": order_item.item.company,
                                         "Категория": order_item.item.category,
                                         "Подкатегория": order_item.item.category,
                                         "Наименование": order_item.item.name,
                                         "Цена товара": order_item.item.get_cool_price(),
                                         "Количество товара": order_item.quantity,
                                         "Cумма": order_item.get_cool_price(),
                                         "Артикул": order_item.item.article})
                df = df.append(item_series, ignore_index=True)

            final_series = pd.Series({"Брэнд": "",
                                      "Категория": "",
                                      "Подкатегория": "",
                                      "Наименование": "",
                                      "Цена товара": "",
                                      "Количество товара": "Сумма",
                                      "Cумма": order.get_cool_price(),
                                      "Артикул": ""})
            df = df.append(final_series, ignore_index=True)
            date = order.date.strftime("%d-%m-%Y_%H-%M-%S")
            writer = pd.ExcelWriter(f"Order-{date}.xlsx", engine='xlsxwriter')
            df.to_excel(writer, sheet_name="Товары", index=False)
            worksheet = writer.sheets['Товары']
            for i, col in enumerate(df.columns):
                # find length of column i
                column_len = df[col].astype(str).str.len().max()
                # Setting the length if the column header is larger
                # than the max column value length
                column_len = max(column_len, len(col))
                # set the column length
                worksheet.set_column(i, i, column_len)
            writer.save()
            writer.close()
            with open(f"Order-{date}.xlsx", 'rb') as exc:
                email.attach_file(exc.name)
            email.send()
            os.remove(f"Order-{date}.xlsx")
            for file in files:
                file.delete()

            folder = os.path.join(BASE_DIR, "static", "cart_files")
            for filename in os.listdir(folder):
                file_path = os.path.join(folder, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))

            return redirect('/')

        else:
            messages.error(self.request, "Введите корректные данные")
            return redirect('/checkout/')



class TestView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):

        context = {
            's_form': SearchForm()
        }
        return render(self.request, "landing/test.html", context)


