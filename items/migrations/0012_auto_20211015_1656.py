# Generated by Django 3.2.4 on 2021-10-15 13:56

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0011_category_subcategory'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='category',
            options={'verbose_name_plural': 'Categories'},
        ),
        migrations.AlterModelOptions(
            name='subcategory',
            options={'verbose_name_plural': 'subcategories'},
        ),
    ]