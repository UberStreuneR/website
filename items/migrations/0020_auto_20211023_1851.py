# Generated by Django 3.2.4 on 2021-10-23 15:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('items', '0019_alter_item_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='item',
            name='name_lowercase',
            field=models.CharField(blank=True, max_length=256),
        ),
        migrations.AlterField(
            model_name='item',
            name='name',
            field=models.CharField(blank=True, max_length=256),
        ),
    ]
