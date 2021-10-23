# Generated by Django 3.2.4 on 2021-10-09 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0002_item_subcategory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='item',
            name='category',
            field=models.CharField(blank=True, choices=[('BLUE-THINGS', 'BLUE-THINGS'), ('BOLTS', 'BOLTS'), ('CORDS', 'CORDS'), ('PIPES', 'PIPES'), ('RIVETS', 'RIVETS'), ('BOILERS', 'BOILERS')], max_length=20),
        ),
        migrations.AlterField(
            model_name='item',
            name='subcategory',
            field=models.CharField(blank=True, choices=[('GAS-BOILERS', 'GAS-BOILERS'), ('ELECTRIC-BOILERS', 'ELECTRIC-BOILERS'), ('PELLET-BOILERS', 'PELLET-BOILERS'), ('WATER-HEATERS', 'WATER-HEATERS')], max_length=20),
        ),
    ]