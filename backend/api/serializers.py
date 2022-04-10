import django.contrib.auth.password_validation as validators
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.hashers import make_password
from django.shortcuts import get_object_or_404
from drf_base64.fields import Base64ImageField

from rest_framework import serializers

from recipes.models import Ingredient, Recipe, RecipeIngredient, Subscribe, Tag

User = get_user_model()
ERR_MSG = 'Не удается войти в систему с предоставленными учетными данными.'


class UserListSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.BooleanField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.follower.filter(author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password',)

    def validate_password(self, password):
        validators.validate_password(password)
        return password


class UserPasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(
        label='Новый пароль')
    current_password = serializers.CharField(
        label='Текущий пароль')

    def validate_current_password(self, current_password):
        user = self.context['request'].user
        if not authenticate(
                username=user.email,
                password=current_password):
            raise serializers.ValidationError(
                ERR_MSG, code='authorization')
        return current_password

    def validate_new_password(self, new_password):
        validators.validate_password(new_password)
        return new_password

    def create(self, validated_data):
        user = self.context['request'].user
        password = make_password(
            validated_data.get('new_password'))
        user.password = password
        user.save()
        return validated_data


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',)


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount')


class RecipeUserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField(
        read_only=True)

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username',
            'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return False
        return user.follower.filter(author=obj).exists()


class RecipeSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    tags = TagSerializer(
        many=True,
        read_only=True)
    author = RecipeUserSerializer(
        read_only=True,
        default=serializers.CurrentUserDefault())
    ingredients = RecipeIngredientSerializer(
        many=True,
        required=True,
        source='recipe')
    is_favorited = serializers.BooleanField(
        read_only=True)
    is_in_shopping_cart = serializers.BooleanField(
        read_only=True)

    class Meta:
        model = Recipe
        fields = '__all__'

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredient_list = []
        for _ in ingredients:
            ingredient = get_object_or_404(
                Ingredient,
                id=_['id'])
            if ingredient in ingredient_list:
                raise serializers.ValidationError(
                    'ингредиент должен быть уникальным.')
            ingredient_list.append(ingredient)
        tags = self.initial_data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тэг для рецепта.')
        for tag_id in tags:
            if not Tag.objects.filter(id=tag_id).exists():
                raise serializers.ValidationError(
                    f'тэга с id = {tag_id} не существует.')
        return data

    def validate_cooking_time(self, cooking_time):
        if int(cooking_time) < 1:
            raise serializers.ValidationError(
                'Время приготовления >= 1.')
        return cooking_time

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Мин. 1 ингредиент в рецепте.')
        for ingredient in ingredients:
            if int(ingredient.get('amount')) < 1:
                raise serializers.ValidationError(
                    'Количество ингредиента >= 1.')
        return ingredients

    def create_ingredients(self, ingredients, recipe):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'), )

    def create(self, validated_data):
        validated_data.pop('recipe')
        tags = self.initial_data.pop('tags')
        ingredients = self.initial_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.create_ingredients(ingredients, recipe)
        return recipe

    def update(self, instance, validated_data):
        validated_data.pop('recipe')
        tags = self.initial_data.pop('tags')
        ingredients = self.initial_data.pop('ingredients')
        if tags:
            instance.tags.set(tags)
        if ingredients:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        return instance


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscribeSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(
        source='author.id')
    email = serializers.EmailField(
        source='author.email')
    username = serializers.CharField(
        source='author.username')
    first_name = serializers.CharField(
        source='author.first_name')
    last_name = serializers.CharField(
        source='author.last_name')
    recipes = serializers.SerializerMethodField()
    is_subscribed = serializers.BooleanField(
        read_only=True)
    recipes_count = serializers.IntegerField(
        read_only=True)

    class Meta:
        model = Subscribe
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = (
            obj.author.recipe.all()[:int(limit)] if limit
            else obj.author.recipe.all())
        return SubscribeRecipeSerializer(
            recipes,
            many=True).data
