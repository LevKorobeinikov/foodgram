# Generated by Django 4.2.16 on 2025-01-17 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0002_alter_recipe_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'default_related_name': 'recipes', 'ordering': ('-pub_date',), 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
    ]
