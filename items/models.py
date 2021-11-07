from django.db import models
from django.shortcuts import reverse
from transliterate import translit
from django.utils.text import slugify

STATUS_CHOICES = (
    ('A', 'Available'),
    ('P', 'Pending'),
    ('N', 'Not available')
)

class Item(models.Model):
    name = models.CharField(max_length=256, blank=True)
    name_lowercase = models.CharField(max_length=256, blank=True)
    price = models.FloatField(default=0, null=True, blank=True)
    company = models.CharField(max_length=200, blank=True)
    category = models.CharField(max_length=200, blank=True)
    subcategory = models.CharField(max_length=200, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=2, blank=True, default='A')
    slug = models.SlugField(blank=True)
    article = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    # url = models.URLField(blank=True, null=True)
    image = models.ImageField(default='static/landing/images/mainpage/default.jpg')

    weight = models.FloatField(blank=True, null=True)
    measure_unit = models.CharField(max_length=50, default="шт.")

    def __str__(self):
        return f"{self.name}, {self.category}, {self.subcategory}"

    def get_absolute_url(self):
        return reverse("item", kwargs={'company': self.company, 'article': self.article})

    def get_cool_price(self):
        if self.price == -1:
            return "Цена не установлена"
        if self.price == -2:
            return "Цена по запросу"
        price = str(self.price)
        values = price.split(".")
        values[1] = values[1][:2]
        int_price = values[0]
        for i in range(3, len(int_price) + 1, 4):
            int_price = int_price[:-i] + " " + int_price[-i:]
        return int_price + " руб."

    def save(self, *args, **kwargs):
        if self.company:
            self.url = self.get_absolute_url()
        self.slug = slugify(translit(self.name, 'ru', reversed=True))
        if self.name:
            if self.name[0] != " " and self.name[:-1] != " ":
                self.name = " " + self.name + " "
            self.name_lowercase = self.name.lower()
        super(Item, self).save(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, category"

    def slugified_name(self):
        return slugify(self.name)

    class Meta:
        verbose_name_plural = 'Categories'


class Subcategory(models.Model):
    name = models.CharField(max_length=256, blank=True, null=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE, blank=True, null=True)
    comment = models.CharField(max_length=512, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.comment}, subcategory"

    class Meta:
        verbose_name_plural = 'subcategories'

