from functools import reduce
from django.core.paginator import Paginator
from django.shortcuts import render, redirect, get_object_or_404, reverse
from django.views.generic import View
from django.db.models import Q
from .models import Item, Category, Subcategory
from landing.models import Order, OrderItem, Partner, File
from clients.models import Client
from django.contrib import messages
from .forms import ExcelItemsForm, SearchForm, HowMuchCounterForm
from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.templatetags.static import static
from landing.forms import OrderDetailsForm, OrderFilesForm
from landing.serializers import OrderSerializer, ItemSerializer, OrderItemSerializer
import os
import json
from pathlib import Path
from transliterate import translit
DIR = Path(__file__).resolve().parent


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
                if changed == "нет" or changed == "":
                    continue
                company = translit(row['Брэнд'], "ru", reversed=True).replace(" ", "_")
                partner = Partner.objects.get_or_create(name=company)[0]
                partner.save()
                category = row['Категория']
                subcategory = row['Подкатегория']
                name = row['Наименование']
                article = row['Артикул']
                price = row['Цена']
                comment = row['Расшифровка подкатегории']
                item, created = Item.objects.get_or_create(article=article)
                try:
                    weight = row['Вес']
                    if weight != "-":
                        item.weight = float(str(weight).replace(",", "."))
                except KeyError:
                    pass
                measure_unit = row['Единица измерения']
                item.measure_unit = measure_unit
                item.company = company
                item.category = category
                item.subcategory = subcategory
                item.price = float(str(price).replace(",", "."))
                item.name = name
                print(name)
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
        try:
            user = self.request.user
            is_staff = user.is_staff
        except:
            is_staff = False
        context = {
            'categories': categories,
            'company': kwargs['company'],
            'is_staff': is_staff
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
            subcategory = items[0].subcategory

        try :
            tile_view = self.request.GET['tile_view']
            paginator = Paginator(items, 6)
            try:
                page_number = self.request.GET.get('page')
            except KeyError:
                page_number = 1
            page_obj = paginator.get_page(page_number)
        except:
            tile_view = False

        s_form = SearchForm()
        h_form = HowMuchCounterForm()

        is_mobile = self.request.user_agent.is_mobile
        context = {
            'items': items,
            'category': category,
            'subcategory': subcategory,
            'categories': Category.objects.filter(company=company),
            'company': company,
            's_form': s_form,
            'h_form': h_form,
            'tile_view': tile_view,
            'is_mobile': is_mobile
        }
        companies = ['Danfoss', 'Uponor', 'Tecofi']
        if company in companies:
            context.update({"add_company": True})
        else:
            context.update({"add_company": False})
        if tile_view:
            context.update({'page_obj': page_obj,
                            'count': page_obj.object_list.count()})
        return render(self.request, "items/categories.html", context)


class DeleteCompanyView(UserPassesTestMixin, LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        company = kwargs['company']
        items = Item.objects.filter(company=company)
        for item in items:
            item.delete()
        try:
            company = Partner.objects.get(name=company)
            company.delete()
        except:
            pass
        return redirect("/")
    def test_func(self):
        return self.request.user.is_staff

class SearchView(View):
    def get(self, *args, **kwargs):
        print()
        print()
        print()
        print()
        print(self.request.GET)
        print()
        print()
        print()
        print()
        try:
            text = self.request.GET['text']
            if " " in text:
                items = Item.objects.filter(Q(article=text)
                                            | Q(company__icontains=text)
                                            | Q(category__icontains=text)
                                            | Q(subcategory__icontains=text)
                                            | reduce(lambda x, y: x & y, [Q(name_lowercase__icontains=" " + word.replace(",", "").lower()+" ") for word in text.split(" ")])
                                            | reduce(lambda x, y: x & y, [Q(name_lowercase__icontains=" " + word.replace(",", "").lower()+",") for word in text.split(" ")]))
            else:
                items = Item.objects.filter(Q(article=text)
                                            | Q(company__icontains=text)
                                            | Q(category__icontains=text)
                                            | Q(subcategory__icontains=text)
                                            | Q(name__icontains=text)
                                            | Q(name_lowercase__icontains=" " + text.lower() + " ")
                                            | Q(name_lowercase__icontains=" " + text.lower() + ","))
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
        unwelcome_companies = ['Detali_truboprovodov', 'Metizy', 'Teploizoljatsija_i_zvukoizoljatsija']
        if company.name in unwelcome_companies:
            welcome = False
        else:
            welcome = True
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

        s_form = SearchForm()
        h_form = HowMuchCounterForm()
        context = {
            'item': item,
            'company': company,
            's_form': s_form,
            'h_form': h_form,
            'welcome': welcome
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
        if order.items.count() == 0:
            return redirect(reverse('cart'))
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
        if order.items.count() == 0:
            return redirect("/")
        if redirect_to is not None:
            return redirect(redirect_to)
        return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")
    else:
        messages.warning(request, "Ошибка, товара не было в корзине")
        if redirect_to is not None:
            return redirect(redirect_to)
        return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")


def add_item_to_cart(request, slug):
    if request.method == "GET":
        return redirect('/cart/')
    if request.method == "POST":
        item = Item.objects.filter(slug=slug)[0]
        form = HowMuchCounterForm(request.POST)
        if form.is_valid():
            by_how_much = form.cleaned_data['counter']

            if by_how_much == 0:
                messages.info(request, "Сколько добавить?")
                return redirect(
                    f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")
            print(by_how_much)

        else:
            messages.warning(request, "Неправильное количество товара")
            return redirect(f'{request.GET["redirect"]}')
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
            order_item.quantity += by_how_much
            order_item.save()
            messages.success(request, "Количество товара в корзине было обновлено")

            if redirect_to is not None:
                return redirect(redirect_to)
            return redirect(f"/items/{item.company}/category/?category={item.category}&subcategory={item.subcategory}")
        else:
            order.items.add(order_item)
            order_item.quantity += by_how_much - 1
            order_item.save()
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
    messages.success(request, "Корзина была очищена")
    return redirect("/")


class Download(View, UserPassesTestMixin, LoginRequiredMixin):

    def get(self, *args, **kwargs):

        company = self.request.GET['company']
        if 'subcategory' in self.request.GET.keys():
            subcategory = self.request.GET['subcategory']
            category = self.request.GET['category']
            items = Item.objects.filter(company=company, category=category, subcategory=subcategory)
        else:
            if 'category' in self.request.GET.keys():
                category = self.request.GET['category']
                items = Item.objects.filter(company=company, category=category)
            else:
                items = Item.objects.filter(company=company)



        df = pd.DataFrame()
        for item in items:
            item_series = pd.Series({"Брэнд": item.company,
                                    "Категория": item.category,
                                    "Подкатегория": item.subcategory,
                                    "Расшифровка подкатегории": "",
                                    "Наименование": item.name,
                                    "Цена": item.price,
                                    "Единица измерения": item.measure_unit,
                                    "Вес": item.weight,
                                    "Артикул": item.article,
                                    "Конечное название": item.company + " " + item.category + " " + item.name + " арт. " + item.article,
                                    "Обновлено": "нет",
                                    "Путь": item.image})
            df = df.append(item_series, ignore_index=True)
        df2 = pd.DataFrame.from_dict(({"Брэнд": [0],
                                       "Категория": [0],
                                       "Подкатегория": [0],
                                       "Расшифровка подкатегории": [0],
                                       'Наименование': [0],
                                       "Цена": [0],
                                       "Единица измерения": [0],
                                       "Вес": [0],
                                       "Конечное название": [0],
                                       "Обновлено": [0],
                                       "Путь": [0]}))
        df = df2.append(df, ignore_index=True)
        df = df.iloc[1:]
        path = os.path.join(DIR, "static", "items", "file.xlsx")

        df.to_excel(path, index=False)
        with open(path, "rb") as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = f'inline;filename={company}.xlsx'
            return response

    def test_func(self):
        return self.request.user.is_staff


def ajax_add_to_cart(request, slug):
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
    if request.method == "POST":
        form = HowMuchCounterForm(request.POST)
        if form.is_valid():
            by_how_much = form.cleaned_data['counter']
            if by_how_much == 0:
                messages.info(request, "Сколько добавить?")
                return JsonResponse({'added': False, 'count': order.items.count()})
            if order.items.filter(item__slug=slug).exists():
                order_item.quantity += by_how_much
                order_item.save()
            else:
                order.items.add(order_item)
                order_item.quantity += by_how_much - 1
                order_item.save()
            return JsonResponse({'added': True, 'count': order.items.count(), 'quantity': order_item.quantity})


def ajax_remove_from_cart(request):
    article = request.POST['article']
    item = Item.objects.filter(article=article)[0]
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
    order_item.delete()
    response = {'success': True, 'cool_price': order.get_cool_price()}

    if order.items.count() == 0:
        response.update({'empty': True})
    else:
        response.update({'empty': False})
    return JsonResponse(response)



def ajax_add_single_to_cart(request, slug):
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
    if request.method == "POST":
        if order.items.filter(item__slug=slug).exists():
            order_item.quantity += 1
            order_item.save()
        else:
            order.items.add(order_item)
            order_item.save()
        return JsonResponse({'added': True,
                             'count': order.items.count(),
                             'quantity': order_item.quantity,
                             'price': order_item.get_cool_price(),
                             'order-price': order.get_cool_price(),
                             'link': item.get_absolute_url(),
                             'name': item.name})



def ajax_remove_single_from_cart(request, slug):
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
    if request.method == "POST":
        if order_item.quantity == 1:
            order.items.remove(order_item)
            order_item.delete()
            price = 0
            redirect = '/cart/'
            quantity = 0
        else:
            order_item.quantity -= 1
            order_item.save()
            price = order_item.get_cool_price()
            redirect = 'None'
            quantity = order_item.quantity
        if order.items.count() == 0:
            redirect = '/'
            quantity = 0
        return JsonResponse({'removed': True, 'quantity': quantity, 'price': price, 'order-price': order.get_cool_price()})

def ajax_save_order_details(request):
    try:
        client = request.user.client
    except:
        device = request.COOKIES['device']
        client, created = Client.objects.get_or_create(device=device)

    order, created = Order.objects.get_or_create(client=client, complete=False)
    if request.method == "POST":
        d_form = OrderDetailsForm(request.POST)
        if d_form.is_valid():
            order.details = d_form.cleaned_data['details']
            order.save()
            return JsonResponse({'saved': True, 'data': d_form.cleaned_data['details']})
        return JsonResponse({'saved': False, 'data': d_form.cleaned_data['details']})

def ajax_get_order_items(request):
    try:
        client = request.user.client
    except:
        device = request.COOKIES['device']
        client, created = Client.objects.get_or_create(device=device)

    order, created = Order.objects.get_or_create(client=client, complete=False)
    if request.method == "GET":
        order_serializer = OrderSerializer(order)
        response = {'order': order_serializer.data}
        if order.items.count() == 0:
            response.update({'empty': True})
        else:
            response.update({'empty': False})
        return JsonResponse(response)
    return JsonResponse({})

class UploadFileToOrderView(View):
    def post(self, *args, **kwargs):
        try:
            client = self.request.user.client
        except:
            device = self.request.COOKIES['device']
            client, created = Client.objects.get_or_create(device=device)
        order, created = Order.objects.get_or_create(client=client, complete=False)
        f_form = OrderFilesForm(self.request.POST, self.request.FILES)
        if f_form.is_valid():
            for file in self.request.FILES.getlist('file'):
                print(file, file.name)
                File.objects.create(file=file, order=order, name=file.name)
        return redirect("/cart/")


def delete_file_from_order(request):
    try:
        client = request.user.client
    except:
        device = request.COOKIES['device']
        client, created = Client.objects.get_or_create(device=device)
    order, created = Order.objects.get_or_create(client=client, complete=False)
    name = request.GET['name']
    file = order.files.filter(Q(name__icontains=name))[0]
    file.delete()
    messages.success(request, "Файл удален")
    return redirect('/cart/')

def update_order_from_side_cart(request):
    try:
        client = request.user.client
    except:
        device = request.COOKIES['device']
        client, created = Client.objects.get_or_create(device=device)
    order, created = Order.objects.get_or_create(client=client, complete=False)
    if request.method == "POST":
        response = {}
        append_to_response = {'items': []}
        for key, value in request.POST.items():
            item = Item.objects.filter(article=key)[0]
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                ordered=False
            )
            order_item.quantity = int(value)
            order_item.save()
            append_to_response['items'].append({str(item.article): order_item.get_cool_price()})
        response.update({'success': True, 'cool_price': order.get_cool_price()})
        response.update(append_to_response)
        return JsonResponse(response)

def ajax_get_all_partners(request):
    companies = ['Uponor', 'Danfoss', 'Tecofi', 'Belimo', 'Rehau', 'SML']
    if request.method == "GET":
        partners = Partner.objects.all()
        partners_list = []
        for partner in partners:
            if partner.name not in companies:
                name = translit(partner.name, 'ru').replace("_", " ")
            else:
                name = partner.name
            partners_list.append({name: f'/items/{partner.name}'})
        return JsonResponse({'partners': partners_list})

def update_order_from_listview(request):
    if request.method == "GET":
        return JsonResponse({"success": "GET request for some reason"})
    try:
        client = request.user.client
    except:
        device = request.COOKIES['device']
        client, created = Client.objects.get_or_create(device=device)
    order, created = Order.objects.get_or_create(client=client, complete=False)
    if request.method == "POST":
        counters_dict = json.loads(request.POST['changed_counters'])
        print(counters_dict)

        for key, value in counters_dict.items():
            item = Item.objects.filter(article=key)[0]
            order_item, created = OrderItem.objects.get_or_create(
                item=item,
                ordered=False
            )
            order_item.quantity = int(value)
            order_item.save()
            if order.items.filter(item__slug=item.slug).exists():
                pass
            else:
                order.items.add(order_item)
                order_item.save()
        return JsonResponse({'success': True})

def test_ajax(request):
    print()
    print()
    print()
    print()
    print()
    print("Test ajax success")
    print(request.POST)
    print(request.GET)
    print()
    print()
    print()
    return JsonResponse({'success': True})