from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from django.utils.text import slugify
from transliterate import translit
import time
import os

import pandas as pd
import requests



NO_H3_SUBSTITUTE = "Трубы из сшитого полиэтилена PE-X, PE-RT и фитинги"

def download(path, link, article, extension):
    print("downloading")
    req = requests.get(link)
    link = f"{path}/{article}.{extension}"
    with open(link, "wb") as file:
        file.write(req.content)
    return link[link.find("static"):]

def isEnglish(s):
    try:
        s.encode(encoding='utf-8').decode('ascii')
    except UnicodeDecodeError:
        return False
    else:
        return True

def to_eng(string):
    result = ""
    still_russian = False

    for letter in string:
        if not letter.isalpha():
            result += letter
            continue
        if isEnglish(letter):
            if still_russian:
                result += "tagRUS"
                still_russian = False
            result += letter
        else:
            if still_russian is False:
                result += "tagRUS"
                still_russian = True
            result += translit(letter, 'ru', reversed=True)
    if still_russian:
        result += "tagRUS"
    return result


def from_eng(string):
    result = ""
    string = string.replace("tagCOMMA", ",")
    while True:
        if "tagRUS" in string:
            before = string[:string.index("tagRUS")]
            string = string[string.index("tagRUS") + 6:]
            between = string[:string.index("tagRUS")]
            string = string[string.index("tagRUS") + 6:]
            result += before + translit(between, 'ru')
        else:
            result += string
            break

    return result


class Category:
    def __init__(self, name):
        self.name = name
        self.subcategories = []

    def __str__(self):
        string = "["
        for subcat in self.subcategories:
            string += subcat.name + " "
        return self.name + " " + string + "]"

class Subcategory:
    def __init__(self, name, comment, link):
        self.name = name
        self.comment = comment
        self.link = link
        self.items = []

    def __str__(self):
        return self.name

class Item:
    def __init__(self, name, price, article, link):
        self.name = name
        self.price = price
        self.article = article
        self.images = []
        self.link = link
    def __str__(self):
        return self.name

class Parser:

    def __init__(self, link, images, images_path, BRAND):
        self.link = link
        self.options = Options()
        self.options.binary_location = "C:/Users/Best User/AppData/Local/Google/Chrome SxS/Application/chrome.exe"
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--disable-gpu')
        # self.options.add_argument(USER_DATA_DIR)
        # self.options.add_extension("uBlock.crx")
        self.options.add_argument("--start-maximized")
        self.driver = webdriver.Chrome(executable_path='D:/Developer/Python/chromedriver-canary.exe',
                                       options=self.options)
        self.categories = []
        self.images = images  # bool
        self.df = pd.DataFrame()
        self.images_path = images_path
        self.BRAND = BRAND


    def __del__(self):
        self.driver.close()

    def start(self):
        self.driver.get(self.link)
        series = self.driver.find_element_by_class_name("brand-serieses")

        # h3s = series.find_elements_by_xpath(".//h3")
        rows = series.find_elements_by_xpath(".//div[@class='row']")
        # for h3 in h3s:
        for row in rows:


            # row = h3.find_element_by_xpath("following-sibling::div")
            try:
                h3 = row.find_elements_by_xpath("preceding-sibling::h3")[-1]
                category_object = Category(h3.text)
                print("row in rows ", h3.text)
            except:
                h3 = NO_H3_SUBSTITUTE
                category_object = Category(h3)
                print("row in rows ", h3)

            self.categories.append(category_object)
            for div in row.find_elements_by_xpath("*"):
                a = div.find_element_by_tag_name("a")
                comment = div.find_element_by_tag_name("div")
                subcategory_object = Subcategory(a.text, comment.text, a.get_attribute("href"))
                category_object.subcategories.append(subcategory_object)

                print("start", a.text, a.get_attribute("href"), comment.text)

    def parse_categories(self):
        cat_count = 0

        for category in self.categories:
            cat_path = os.path.join(IMAGES_PATH, str(cat_count))
            cat_count += 1
            try:
                os.mkdir(cat_path)
            except:
                pass

            subcat_count = 0

            for subcategory in category.subcategories:
                sub_path = os.path.join(cat_path, str(subcat_count))
                subcat_count += 1
                try:
                    os.mkdir(sub_path)
                except:
                    pass
                self.driver.get(subcategory.link)
                iterations = int(len(self.driver.find_elements_by_class_name("menu-pagination-item"))/2)
                if iterations == 0:
                    iterations = 1
                for i in range(1, iterations+1):
                    self.driver.get(subcategory.link + f"/page-{i}")
                    try:
                        row = self.driver.find_element_by_class_name("row.category-products.category-products-4")
                    except:
                        continue
                    for product in row.find_elements_by_class_name("category-products-product"):
                        a = product.find_element_by_class_name("category-products-product-image").find_element_by_tag_name("a")
                        link = a.get_attribute("href")
                        image_link = a.get_attribute("style")
                        image_link = "https://vodokomfort.ru" + image_link[image_link.find("url") + 5: -3]
                        # print(f"'{image_link}'")
                        name = product.find_element_by_class_name("category-products-product-name").text
                        price = product.find_element_by_class_name("product-price")
                        if len(price.find_elements_by_class_name("product-price-percent")) > 0:
                            price = price.text
                            price = price[price.find("ц") + 6:]
                            price = price[price.find("\n") + 1:]
                        else:
                            price = price.text
                            price = price[price.find("ц") + 6:]
                        if price != "":
                            if "запрос" not in price:
                                price = float(price[:price.find("₽")].replace(" ", ""))
                            else:
                                price = -2 # Цена по запросу
                        else:
                            price = -1 # Нет цены
                        article = product.find_element_by_class_name("category-products-product-code").text
                        article = article[article.find(" ") + 1:]
                        file_path = ""
                        if self.images:
                            if image_link.find(".jpg") != -1:
                                file_path = download(sub_path, image_link, article, "jpg")
                            if image_link.find(".jpeg") != -1:
                                file_path = download(sub_path, image_link, article, "jpeg")
                            if image_link.find(".png") != -1:
                                file_path = download(sub_path, image_link, article, "png")

                        print("parse", link, price, article)
                        item = Item(name, price, article, link)
                        item_series = pd.Series({"Брэнд": self.BRAND,
                                                 "Категория": category.name,
                                                 "Подкатегория": subcategory.name,
                                                 "Расшифровка подкатегории": subcategory.comment,
                                                 "Наименование": name,
                                                 "Цена": price,
                                                 "Единица измерения": "шт.",
                                                 "Вес": -1,
                                                 "Артикул": article,
                                                 "Конечное название": self.BRAND + " " + category.name + " " + name + " арт. " + article,
                                                 "Обновлено": "да",
                                                 "Путь": file_path})
                        self.df = self.df.append(item_series, ignore_index=True)

        # Сортировка
        df2 = pd.DataFrame.from_dict(({"Брэнд": self.BRAND,
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
        self.df = df2.append(self.df, ignore_index=True)
        self.df = self.df.iloc[1:]

# BRANDS = ['Uponor']
BRANDS = ['Danfoss', 'Uponor', 'Tecofi']
for brand in BRANDS:
    IMAGES_PATH = r"C:\Users\Public\Developer\Python\PycharmProjects\website\items\static\items\images\{0}".format(brand)
    link = f'https://vodokomfort.ru/brand/{brand.lower()}'

    parser = Parser(link, images=True, images_path=IMAGES_PATH, BRAND=brand)
    parser.start()
    parser.parse_categories()
    parser.df.to_excel(f"{brand}.xlsx", sheet_name="Товары", index=False)