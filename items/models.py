from django.db import models
from django.shortcuts import reverse
from transliterate import translit
from django.utils.text import slugify

ITEM_CATEGORIES = (
    ('BT', 'BLUE-THINGS'),
    ('B', 'BOLTS'),
    ('C', 'CORDS'),
    ('P', 'PIPES'),
    ('R', 'RIVETS'),
    ('BL', 'BOILERS'),

)

STATUS_CHOICES = (
    ('A', 'Available'),
    ('P', 'Pending'),
    ('N', 'Not available')
)

class Item(models.Model):
    name = models.CharField(max_length=50)
    price = models.IntegerField()
    category = models.CharField(choices=ITEM_CATEGORIES, max_length=2, blank=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=2, blank=True)
    slug = models.SlugField(blank=True)
    description = models.TextField(blank=True)

    def get_absolute_url(self):
        return reverse("comm", kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        self.slug = slugify(translit(self.name, 'ru', reversed=True))
        super(Item, self).save(args, kwargs)