from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import View, DetailView
from .models import Item, Category, Subcategory
from landing.models import Order, OrderItem, Partner
from clients.models import Client
from django.contrib import messages
from .forms import ExcelItemsForm, ArticleSearchForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import pandas as pd
from django.templatetags.static import static
import os


def get_image_path(company, category, subcategory, article):
    PATH = r"C:\Users\Public\Developer\Python\PycharmProjects\website\items\static\items\images\{0}".format(str(company))
    PATH = os.path.join(PATH, category, subcategory.replace("/", "^"))
    for i in os.walk(PATH):
        for file in i[2]:
            if article in file:
                to_return = os.path.join(PATH, file)
                to_return = to_return[to_return.find("static"):]
                return to_return


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
                try:
                    path = get_image_path(company, category, subcategory, str(article)).replace("\\", "/")
                    item.image = path
                except AttributeError:
                    pass
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
        form = ArticleSearchForm()
        context = {
            'items': items,
            'category': category,
            'categories': Category.objects.filter(company=company),
            'company': company,
            'form': form
        }

        return render(self.request, "items/categories.html", context)


class ItemView(View):
    def get(self, *args, **kwargs):
        item = get_object_or_404(Item, company=kwargs['company'], article=kwargs['article'])
        company = get_object_or_404(Partner, name=kwargs['company'])
        form = ArticleSearchForm()
        context = {
            'item': item,
            'company': company,
            'form': form
        }
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
