from datetime import date


def shopping_list_to_txt(ingredients, recipes):
    return '\n'.join([
        f'Список покупок на {date.today()}:',
        'Продукты:',
        *[
            f'{index + 1}.'
            f'{ingredient['ingredient__name'].capitalize()} -'
            f'{ingredient['sum']}'
            f'{ingredient['ingredient__measurement_unit']}'
            for index, ingredient in enumerate(ingredients)
        ],
        'Рецепты:',
        *[
            f'- {recipe}' for recipe in recipes
        ]
    ])
