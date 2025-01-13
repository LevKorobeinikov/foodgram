from datetime import date

SHOPPING_LIST_TEMPLATE = (
    'Список покупок на {today}:\n'
    'Продукты:\n'
    '{products}\n'
    'Рецепты:\n'
    '{recipes}\n'
)
PRODUCTS = '{index}. {name} - {amount} {unit}'
RECIPES = '- {recipe}'


def shopping_list_to_txt(ingredients, recipes):
    products = '\n'.join(
        PRODUCTS.format(
            index=index,
            name=ingredient['ingredient__name'].capitalize(),
            amount=ingredient['sum'],
            unit=ingredient['ingredient__measurement_unit'],
        )
        for index, ingredient in enumerate(ingredients, start=1)
    )
    recipes = '\n'.join(
        RECIPES.format(recipe=recipe) for recipe in recipes
    )
    return SHOPPING_LIST_TEMPLATE.format(
        today=date.today(),
        products=products,
        recipes=recipes,
    )
