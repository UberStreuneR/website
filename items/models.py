from django.db import models
from django.shortcuts import reverse
from transliterate import translit
from django.utils.text import slugify

COMPANIES = (
    ('danfoss', 'danfoss'),
)


ITEM_CATEGORIES = (
    ('BLUE-THINGS', 'BLUE-THINGS'),
    ('BOLTS', 'BOLTS'),
    ('CORDS', 'CORDS'),
    ('PIPES', 'PIPES'),
    ('RIVETS', 'RIVETS'),
    ('BOILERS', 'BOILERS'),

)

ITEM_SUBCATEGORIES = (
    ('GAS-BOILERS', 'GAS-BOILERS'),
    ('ELECTRIC-BOILERS', 'ELECTRIC-BOILERS'),
    ('PELLET-BOILERS', 'PELLET-BOILERS'),
    ('WATER-HEATERS', 'WATER-HEATERS'),
    # THE REST OF THEM
)

STATUS_CHOICES = (
    ('A', 'Available'),
    ('P', 'Pending'),
    ('N', 'Not available')
)



class Item(models.Model):
    name = models.CharField(max_length=50, blank=True)
    price = models.FloatField(default=0, null=True, blank=True)
    company = models.CharField(max_length=20, blank=True)
    category = models.CharField(max_length=50, blank=True)
    subcategory = models.CharField(max_length=20, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=2, blank=True, default='A')
    slug = models.SlugField(blank=True)
    article = models.CharField(max_length=30, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"{self.name}, {self.category}, {self.subcategory}"

    def get_absolute_url(self):
        return reverse("comm", kwargs={'slug': self.slug})

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