# Generated by Django 3.2.4 on 2021-11-01 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0022_auto_20211028_1849'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='item',
            name='company',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='item',
            name='subcategory',
            field=models.CharField(blank=True, max_length=200),
        ),
    ]