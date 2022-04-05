import django_filters as filters
from django.core.exceptions import ValidationError
from django_filters.fields import MultipleChoiceField

from recipes.models import Ingredient, Recipe


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(
        lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name',)


class TagsMultipleChoiceField(MultipleChoiceField):
    def validate(self, value):
        if self.required and not value:
            raise ValidationError(
                self.error_messages['required'],
                code='required')
        for val in value:
            if val in self.choices and not self.valid_value(val):
                raise ValidationError(
                    self.error_messages['invalid_choice'],
                    code='invalid_choice',
                    params={'value': val},)


class TagsFilter(filters.AllValuesMultipleFilter):
    field_class = TagsMultipleChoiceField


# ! READY
class RecipeFilter(filters.FilterSet):
    is_favorited = filters.BooleanFilter(
        field_name='is_favorited',
        label='В избранном',)
    is_in_shopping_cart = filters.BooleanFilter(
        field_name='is_in_shopping_cart',
        label='В корзине',)
    tags = TagsFilter(
        field_name='tags__slug',
        label='Слаг тэга',)

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'author', 'is_in_shopping_cart', 'tags',)
