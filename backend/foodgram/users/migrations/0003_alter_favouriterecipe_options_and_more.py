# Generated by Django 4.2.7 on 2023-11-27 20:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_follow_date_added_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='favouriterecipe',
            options={'ordering': ['-date_added', 'user'], 'verbose_name': 'Избранный товар', 'verbose_name_plural': 'Избранное'},
        ),
        migrations.AlterModelOptions(
            name='shoppingcard',
            options={'ordering': ['-date_added', 'user'], 'verbose_name': 'Товар в корзине', 'verbose_name_plural': 'Корзины'},
        ),
    ]