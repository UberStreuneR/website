from functools import reduce

from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View
from django.db.models import Q
from .models import Item, Category, Subcategory
from landing.models import Order, OrderItem, Partner
from clients.models import Client
from django.contrib import messages
from .forms import ExcelItemsForm, SearchForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import pandas as pd
from django.templatetags.static import static
import os
from pathlib import Path
from transliterate import translit
DIR = Path(__file__).resolve().parent

# def get_image_path(company, category, subcategory, article):
#     PATH = os.path.join(DIR, "static", "items", "images", company)
#     PATH = os.path.join(PATH, category.replace(" ", "_").replace(",", "tagCOMMA"), subcategory.replace("/", "^").replace(" ", "_"))
#     for i in os.walk(PATH):
#         for file in i[2]:
#             if article in file:
#                 to_return = os.path.join(PATH, file)
#                 to_return = to_return[to_return.find("static"):]
#                 return to_return
#
#
# def isEnglish(s):
#     try:
#         s.encode(encoding='utf-8').decode('ascii')
#     except UnicodeDecodeError:
#         return False
#     else:
#         return True
#
# def to_eng(string):
#     result = ""
#     still_russian = False
#     for letter in string:
#         if not letter.isalpha():
#             result += letter
#             continue
#         if isEnglish(letter):
#             if still_russian:
#                 result += "tagRUS"
#                 still_russian = False
#             result += letter
#         else:
#             if still_russian is False:
#                 result += "tagRUS"
#                 still_russian = True
#             result += translit(letter, 'ru', reversed=True)
#     if still_russian:
#         result += "tagRUS"
#     return result
#
#
# def from_eng(string):
#     result = ""
#     while True:
#         if "tagRUS" in string:
#             before = string[:string.index("tagRUS")]
#             string = string[string.index("tagRUS") + 6:]
#             between = string[:string.index("tagRUS")]
#             string = string[string.index("tagRUS") + 6:]
#             result += before + translit(between, 'ru')
#         else:
#             result += string
#             break
#
#     return result


class UploadItemsView(UserPassesTestMixin, LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = ExcelItemsForm()
        context = {
            'form': form,
            'title': 'upload'
        }
        return render(self.request, "items/upload.html", context)

    def post(self, *args, **kwargs):
        form = ExcelItemsForm(self.request.POST, self.request.FILES)
        if form.is_valid():

            xl = form.cleaned_data['file']
            df = pd.read_excel(xl)

            for i in range(len(df.index)):
                print(i, " out of ", df.index)
                row = df.iloc[i]
                changed = row['Обновлено']
                if changed == "нет":
                    continue
                company = row['Брэнд']
                category = row['Категория']
                subcategory = row['Подкатегория']
                name = row['Наименование']
                article = row['Артикул']
                price = row['Цена']
                comment = row['Расшифровка подкатегории']
                item = Item.objects.get_or_create(article=article)[0]
                item.company = company
                item.category = category
                item.subcategory = subcategory
                item.price = price
                item.name = name
                path = row['Путь']
                if type(path) == str:
                    item.image = path
                # path = get_image_path(company, to_eng(category), to_eng(subcategory), str(article)).replace("\\", "/")

                item.save()

                CategoryObject, created = Category.objects.get_or_create(name=category, company=company)
                Subcategory.objects.get_or_create(name=subcategory, category=CategoryObject, comment=comment)

            messages.success(self.request, "Файл был загружен, база данных обновлена")
            return redirect("/home/")
        else:
            messages.warning(self.request, "Ошибка загрузки")
            return redirect("/upload/")

    def test_func(self):
        return self.request.user.is_staff


class CompanyListView(View):
    def get(self, *args, **kwargs):
        categories = Category.objects.filter(company=kwargs['company'])

        context = {
            'categories': categories,
            'company': kwargs['company']
        }
        return render(self.request, "items/company.html", context)


class CategoryListView(View):
    def get(self, *args, **kwargs):
        company = kwargs['company']
        try:
            category = self.request.GET['category']
            subcategory = self.request.GET['subcategory']
            items = Item.objects.filter(company=company, category=category, subcategory=subcategory)
        except KeyError:
            article = self.request.GET['article']
            items = Item.objects.filter(company=company, article=article)
            if items.count() == 0:
                messages.warning(self.request, "Неправильный артикул")
                return redirect("/")
            category = items[0].category
        form = SearchForm()
        context = {
            'items': items,
            'category': category,
            'categories': Category.objects.filter(company=company),
            'company': company,
            'form': form
        }
        return render(self.request, "items/categories.html", context)


class SearchView(View):
    def get(self, *args, **kwargs):
        print(self.request.GET)
        try:
            text = self.request.GET['text']
            if " " in text:
                items = Item.objects.filter(Q(article=text)
                                            | Q(company=text)
                                            | Q(category=text)
                                            | Q(subcategory=text)
                                            | reduce(lambda x, y: x & y, [Q(name_lowercase__icontains=" " + word.replace(",", "").lower()+" ") for word in text.split(" ")]))
            else:
                items = Item.objects.filter(Q(article=text)
                                            | Q(company=text)
                                            | Q(category=text)
                                            | Q(subcategory=text)
                                            | Q(name_lowercase__icontains=" " + text.lower() + " "))
        except:
            messages.warning(self.request, "По запросу ничего не найдено")
            return redirect("/")
        form = SearchForm()
        context = {
            'form': form,
            'items': items
        }
        return render(self.request, "items/search.html", context)


class ItemView(View):
    def get(self, *args, **kwargs):
        item = get_object_or_404(Item, article=kwargs['article'])
        company = get_object_or_404(Partner, name=kwargs['company'])

        dn_du = ['dn', 'Dn', 'dN', 'DN',
                 'du', 'Du', 'dU', 'DU',
                 'дн', 'Дн', "дН", "ДН",
                 'ду', "Ду", "дУ", "ДУ"]
        string = item.name
        is_in_name = False
        for variation in dn_du:
            if variation in string:
                is_in_name = True
                to_cut = variation
                count = 2
                while True:
                    try:
                        letter = string[string.find(variation) + count]
                        if letter.isdigit() or letter == " ":
                            count += 1
                        else:
                            break
                    except IndexError:
                        string = string.replace(string[string.find(variation) - 1:], "")
                if string[string.find(variation) + 2] == " ":
                    count = 3
                    to_cut += " "
                elif string[string.find(variation) + 2].isdigit():
                    count = 2
                while True:
                    char = string[string.find(variation) + count]
                    if char.isdigit():
                        to_cut += char
                        count += 1
                    else:
                        break
                string = string.replace(to_cut + " ", "")
                break
        if is_in_name:
            string_keys = string.split(" ")
            print(string_keys)
            qs = Item.objects.filter(
                reduce(lambda x, y: x & y, [Q(name__icontains=word.replace(",", "")) for word in string_keys]))

        else:
            qs = None

        form = SearchForm()
        context = {
            'item': item,
            'company': company,
            'form': form,

        }
        if is_in_name:
            context.update({'related_items': qs})
        return render(self.request, "items/item.html", context)




def remove_item_from_cart(request, slug):
    item = Item.objects.filter(slug=slug)[0]
    try:
        client = request.user.client
    except:
        device = request.COOKIES['device']
        client, created = Client.objects.get_or_create(device=device)

    order = Order.objects.get(client=client, complete=False)
    order_item = OrderItem.objects.get(
        item=item,
        ordered=False
    )

    try:
        redirect_to = request.GET['redirect_to']
    except:
        redirect_to = None

    if order.items.filter(item__slug=slug).exists():
        order.items.remove(order_item)
        order_item.delete()
        messages.success(request, "Товар был удален из корзины")

        if redirect_to is not None:
            return redirect(redirect_to)
        return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")
    else:
        messages.warning(request, "Ошибка, товара не было в корзине")
        if redirect_to is not None:
            return redirect(redirect_to)
        return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")


def remove_single_item_from_cart(request, slug):
    item = Item.objects.filter(slug=slug)[0]
    try:
        client = request.user.client
    except:
        device = request.COOKIES['device']
        client, created = Client.objects.get_or_create(device=device)

    order = Order.objects.get(client=client, complete=False)
    order_item = OrderItem.objects.get(
        item=item,
        ordered=False
    )

    try:
        redirect_to = request.GET['redirect_to']
    except:
        redirect_to = None

    if order.items.filter(item__slug=slug).exists():
        if order_item.quantity == 1:

            order.items.remove(order_item)
            order_item.delete()
            messages.success(request, "Товар был удален из корзины")
        else:
            order_item.quantity -= 1
            order_item.save()
            messages.success(request, "Количество товара в корзине было обновлено")
        if redirect_to is not None:
            return redirect(redirect_to)
        return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")
    else:
        messages.warning(request, "Ошибка, товара не было в корзине")
        if redirect_to is not None:
            return redirect(redirect_to)
        return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")


def add_item_to_cart(request, slug):
    item = Item.objects.filter(slug=slug)[0]
    try:
        client = request.user.client
    except:
        device = request.COOKIES['device']
        client, created = Client.objects.get_or_create(device=device)

    order, created = Order.objects.get_or_create(client=client, complete=False)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        ordered=False
    )

    try:
        redirect_to = request.GET['redirect_to']
    except:
        redirect_to = None


    if order.items.filter(item__slug=slug).exists():
        order_item.quantity += 1
        order_item.save()
        messages.success(request, "Количество товара в корзине было обновлено")

        if redirect_to is not None:
            return redirect(redirect_to)
        return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")
    else:
        order.items.add(order_item)
        messages.success(request, "Товар был добавлен в корзину")
        # TODO
        # return redirect("comm", slug=slug)
        if redirect_to is not None:
            return redirect(redirect_to)
        return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")


def discard_cart(request):
    try:
        client = request.user.client
    except:
        device = request.COOKIES['device']
        client, created = Client.objects.get_or_create(device=device)
    order = get_object_or_404(Order, client=client, complete=False)
    for order_item in order.items.all():
        order_item.delete()
        order.items.remove(order_item)
        order.save()
    messages.success(request, "Your cart was discarded")
    return redirect("/")
