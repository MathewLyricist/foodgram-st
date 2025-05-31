import pytest

from tests.utils.models import recipe_ingredients_model, recipe_model
from tests.utils.recipe import IMAGE

Recipe = recipe_model()
RecipeIngredients = recipe_ingredients_model()


def create_recipe(data: dict):
    ingredients = data.pop('ingredients')
    recipe = Recipe.objects.create(
        author=data['author'],
        name=data['name'],
        image=data['image'],
        text=data['text'],
        cooking_time=data['cooking_time']
    )

    RecipeIngredients.objects.bulk_create([
        RecipeIngredients(
            recipe=recipe,
            ingredient=ingredient['id'],
            amount=ingredient['amount']
        ) for ingredient in ingredients
    ])
    return recipe


@pytest.fixture
def first_recipe(ingredients, second_user):
    return create_recipe({
        'author': second_user,
        'name': 'Пицца домашняя',
        'image': IMAGE,
        'text': 'Готовим вкусную пиццу',
        'cooking_time': 30,
        'ingredients': [
            {'id': ingredients[0], 'amount': 300},
            {'id': ingredients[1], 'amount': 200},
        ]
    })


@pytest.fixture
def second_recipe(ingredients, second_user):
    return create_recipe({
        'author': second_user,
        'name': 'Паста карбонара',
        'image': IMAGE,
        'text': 'Итальянская классика',
        'cooking_time': 20,
        'ingredients': [
            {'id': ingredients[0], 'amount': 250},
            {'id': ingredients[1], 'amount': 150},
        ]
    })


@pytest.fixture
def third_recipe(ingredients, second_user):
    return create_recipe({
        'author': second_user,
        'name': 'Салат цезарь',
        'image': IMAGE,
        'text': 'Легкий и вкусный салат',
        'cooking_time': 15,
        'ingredients': [
            {'id': ingredients[0], 'amount': 200}
        ]
    })


@pytest.fixture
def fourth_recipe(ingredients, second_user):
    return create_recipe({
        'author': second_user,
        'name': 'Жареная картошка',
        'image': IMAGE,
        'text': 'Хрустящая снаружи, мягкая внутри',
        'cooking_time': 25,
        'ingredients': [
            {'id': ingredients[0], 'amount': 500}
        ]
    })


@pytest.fixture
def fifth_recipe(ingredients, second_user):
    return create_recipe({
        'author': second_user,
        'name': 'Гречневая каша',
        'image': IMAGE,
        'text': 'С маслом и зеленью',
        'cooking_time': 35,
        'ingredients': [
            {'id': ingredients[1], 'amount': 200}
        ]
    })


@pytest.fixture
def another_author_recipe(ingredients, first_user):
    return create_recipe({
        'author': first_user,
        'name': 'Омлет с зеленью',
        'image': IMAGE,
        'text': 'Нежный завтрак',
        'cooking_time': 10,
        'ingredients': [
            {'id': ingredients[0], 'amount': 100}
        ]
    })


@pytest.fixture
def secound_author_recipes(first_recipe, second_recipe, third_recipe, fourth_recipe, fifth_recipe) -> list:
    return [first_recipe, second_recipe, third_recipe, fourth_recipe, fifth_recipe]


@pytest.fixture
def all_recipes(secound_author_recipes, another_author_recipe) -> list:
    return [*secound_author_recipes, another_author_recipe]