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
    name = models.CharField(max_length=100, blank=True)
    price = models.FloatField(default=0, null=True, blank=True)
    company = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=50, blank=True)
    subcategory = models.CharField(max_length=20, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=2, blank=True, default='A')
    slug = models.SlugField(blank=True)
    article = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)
    image = models.ImageField(default='static/landing/images/mainpage/default.jpg')

    def __str__(self):
        return f"{self.name}, {self.category}, {self.subcategory}"

    def get_absolute_url(self):
        return reverse("item", kwargs={'company': 'Danfoss', 'article': self.article})

    def get_cool_price(self):
        price = str(self.price)
        values = price.split(".")
        values[1] = values[1][:2]
        int_price = values[0]
        for i in range(3, len(int_price) + 1, 4):
            int_price = int_price[:-i] + " " + int_price[-i:]
        return int_price + "," + values[1]

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(self.name, 'ru', reversed=True))
        super(Item, self).save(*args, **kwargs)

class Category(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    company = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, category"

    def slugified_name(self):
        return slugify(self.name)

    class Meta:
        verbose_name_plural = 'Categories'





class Subcategory(models.Model):
    name = models.CharField(max_length=50, blank=True, null=True)
    category = models.ForeignKey(Category, related_name='subcategories', on_delete=models.CASCADE, blank=True, null=True)
    comment = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.name}, {self.comment}, subcategory"

    class Meta:
        verbose_name_plural = 'subcategories'