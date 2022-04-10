import django_filters as filters
from django.core.exceptions import ValidationError
from django_filters import AllValuesMultipleFilter
from django_filters import rest_framework as filters
from django_filters.fields import MultipleChoiceField
from django_filters.widgets import BooleanWidget
from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class RecipeFilter(filters.FilterSet):
    is_in_shopping_cart = filters.BooleanFilter(
        widget=BooleanWidget(),
        label='В корзине.')
    is_favorited = filters.BooleanFilter(
        widget=BooleanWidget(),
        label='В избранных.')
    tags = AllValuesMultipleFilter(
        field_name='tags__slug',
        label='Ссылка')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart']
