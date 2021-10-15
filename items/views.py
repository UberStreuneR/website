from django.shortcuts import render, redirect
from django.views.generic import View
from .models import Item, Category, Subcategory
from landing.models import Order, OrderItem
from clients.models import Client
from django.contrib import messages
from .forms import ExcelItemsForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import pandas as pd

#UserPassesTestMixin
class UploadItemsView(UserPassesTestMixin, LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        form = ExcelItemsForm()
        context = {
            'form': form
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
        category = self.request.GET['category']

        subcategory = self.request.GET['subcategory']

        items = Item.objects.filter(company=company, category=category, subcategory=subcategory)
        context = {
            'items': items,
            'category': category,
            'categories': Category.objects.all(),
            'company': company
        }


        return render(self.request, "items/categories.html", context)



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

    if order.items.filter(item__slug=slug).exists():
        order_item.quantity += 1
        order_item.save()
        messages.success(request, "Количество товара в корзине было обновлено")
        return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")
    else:
        order.items.add(order_item)
        messages.success(request, "Товар был добавлен в корзину")
        # TODO
        # return redirect("comm", slug=slug)
        return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")


