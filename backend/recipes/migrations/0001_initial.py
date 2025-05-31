import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import core.utils
import recipes.models.fields


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True, verbose_name='Наименование ингредиента')),
                ('measurement_unit', models.CharField(max_length=64, verbose_name='Единицы измерений')),
            ],
            options={
                'verbose_name': 'ингредиент',
                'verbose_name_plural': 'Ингредиенты',
                'db_table': 'cookbook_ingredient',
                'ordering': ['name'],
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256, verbose_name='Наименование рецепта')),
                ('image', models.ImageField(blank=True, upload_to='recipes/images/', verbose_name='Путь до картинки')),
                ('text', models.TextField(verbose_name='Описание')),
                ('cooking_time', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Время не может быть меньше 1 минуты.')], verbose_name='Время приготовления (в минутах)')),
                ('short_link', models.CharField(default=core.utils.generate_short_link, max_length=6, verbose_name='Короткая ссылка')),
                ('pub_date', models.DateTimeField(default=django.utils.timezone.now, editable=False, verbose_name='Дата публикации')),
                ('author', recipes.models.fields.UserForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipes', to=settings.AUTH_USER_MODEL, verbose_name='Автор рецепта')),
            ],
            options={
                'verbose_name': 'рецепт',
                'verbose_name_plural': 'Рецепты',
                'db_table': 'cookbook_recipe',
                'ordering': ['name'],
                'abstract': False,
                'default_related_name': 'recipes',
            },
        ),
        migrations.CreateModel(
            name='ShoppingCart',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', recipes.models.fields.UserForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to=settings.AUTH_USER_MODEL, verbose_name='Владелец корзины покупок')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shopping_cart', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'рецепт к покупке',
                'verbose_name_plural': 'Корзина покупок',
                'db_table': 'cookbook_shopping_cart',
                'abstract': False,
                'default_related_name': 'shopping_cart',
            },
        ),
        migrations.CreateModel(
            name='RecipeIngredients',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1, message='Количество должно быть равно 1 или больше.')], verbose_name='Количество в рецепте')),
                ('ingredient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.ingredient', verbose_name='Ингредиент')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_ingredients', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'ингредиент рецепта',
                'verbose_name_plural': 'Связь ингредиентов с рецептами',
                'db_table': 'cookbook_recipe_ingredients',
                'abstract': False,
                'default_related_name': 'recipe_ingredients',
            },
        ),
        migrations.CreateModel(
            name='RecipeFavorite',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('author', recipes.models.fields.UserForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_favorite', to=settings.AUTH_USER_MODEL, verbose_name='Владелец корзины покупок')),
                ('recipe', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='recipe_favorite', to='recipes.recipe', verbose_name='Рецепт')),
            ],
            options={
                'verbose_name': 'избранный рецепт',
                'verbose_name_plural': 'Избранные рецепты',
                'db_table': 'cookbook_recipe_favorite',
                'abstract': False,
                'default_related_name': 'recipe_favorite',
            },
        ),
        migrations.AddField(
            model_name='recipe',
            name='ingredients',
            field=models.ManyToManyField(related_name='recipes', through='recipes.RecipeIngredients', to='recipes.Ingredient', verbose_name='Ингредиенты'),
        ),
        migrations.AddConstraint(
            model_name='shoppingcart',
            constraint=models.UniqueConstraint(fields=('author', 'recipe'), name='unique_shopping_cart'),
        ),
        migrations.AddConstraint(
            model_name='recipefavorite',
            constraint=models.UniqueConstraint(fields=('author', 'recipe'), name='unique_recipe_favorite'),
        ),
    ]
