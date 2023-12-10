# Generated by Django 4.2.7 on 2023-12-09 11:04

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_alter_recipe_text'),
        ('users', '0002_rename_shoppingcard_shoppingcart'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='FavouriteRecipe',
            new_name='FavoriteRecipe',
        ),
        migrations.RemoveField(
            model_name='user',
            name='favourites',
        ),
        migrations.AddField(
            model_name='user',
            name='favorites',
            field=models.ManyToManyField(related_name='user_favorites', through='users.FavoriteRecipe', to='recipes.recipe', verbose_name='Избранное'),
        ),
    ]