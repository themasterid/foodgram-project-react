from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.aggregates import Count
from django.db.models.expressions import Exists, OuterRef, Value
from django.shortcuts import get_object_or_404
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import api_view
from rest_framework.mixins import CreateModelMixin
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrAdminOrReadOnly

from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscribeRecipeSerializer, SubscribeSerializer,
                          TagSerializer, TokenSerializer, UserCreateSerializer,
                          UserListSerializer, UserPasswordSerializer)

User = get_user_model()


# ! USERS ------------------------------------
# ! READY
class RegisterAndUserList(generics.ListCreateAPIView):
    '''Регистрация (POST) и список пользователей (GET).'''
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return (
            User.objects.annotate(
                is_subscribed=Exists(
                    self.request.user.follower.filter(
                        following=OuterRef('id'))
                )
            ).prefetch_related('follower', 'following')
            if self.request.user.is_authenticated
            else User.objects.annotate(is_subscribed=Value(False)))

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UserCreateSerializer
        return UserListSerializer


# ! READY
class UserDetail(generics.RetrieveAPIView):
    '''Профиль пользователя.'''
    serializer_class = UserListSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return (
            User.objects.annotate(
                is_subscribed=Exists(
                    self.request.user.follower.filter(following=OuterRef('id'))
                )
            ).prefetch_related('follower', 'following')
            if self.request.user.is_authenticated
            else User.objects.annotate(is_subscribed=Value(False)))


# ! READY
@api_view(['GET'])
def about_me(request):
    '''Информация о текущем пользователе.'''
    serializer = UserListSerializer(request.user)
    return Response(
        serializer.data,
        status=status.HTTP_200_OK)


# ! READY
@api_view(['POST'])
def set_password(request):
    '''Изменение пароля текущего пользователя.'''
    serializer = UserPasswordSerializer(
        data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ! READY
class AuthToken(ObtainAuthToken):
    '''Получить токен авторизации.'''
    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, _ = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key}, status=status.HTTP_201_CREATED)


# ! READY
@api_view(['POST'])
def logout(request):
    '''Удаляет токен текущего пользователя.'''
    get_object_or_404(Token, user=request.user).delete()
    return Response(status=status.HTTP_204_NO_CONTENT)
# ! USERS ------------------------------------


# ! TAGS ------------------------------------
# ! READY
class TagList(generics.ListAPIView):
    '''Cписок тегов.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


# ! READY
class TagDetail(generics.RetrieveAPIView):
    '''Получение деталей тега.'''
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
# ! TAGS ------------------------------------


# ! RECIPE ----------------------------------
# ! READY
class RecipeList(generics.ListCreateAPIView):
    '''
    Список рецептов (GET). Страница доступна всем пользователям.
    Доступна фильтрация по избранному, автору,
    списку покупок и тегам.
    '''
    serializer_class = RecipeSerializer
    filterset_class = RecipeFilter
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Recipe.objects.annotate(
                is_in_shopping_cart=Value(False),
                is_favorited=Value(False),
            ).select_related(
                'author'
            ).prefetch_related(
                'tags', 'ingredients', 'recipe',
                'shopping_cart', 'favorite_recipe'
            )

        return Recipe.objects.annotate(
            is_favorited=Exists(FavoriteRecipe.objects.filter(
                user=self.request.user, recipe=OuterRef('id'))
            ),
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                user=self.request.user, recipe=OuterRef('id'))
            )
        ).select_related(
            'author'
        ).prefetch_related(
            'tags', 'ingredients', 'recipe',
            'shopping_cart', 'favorite_recipe'
        )

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# ! READY
class GetUpdateDeleteRecipe(generics.RetrieveUpdateDestroyAPIView):
    '''
    Получение рецепта (GET)
    Обновление рецепта (PATCH)
    Удаление рецепта (DEL)
    Доступно только автору данного рецепта
    '''
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthorOrAdminOrReadOnly,)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return Recipe.objects.annotate(
                is_in_shopping_cart=Value(False),
                is_favorited=Value(False),
            ).select_related(
                'author'
            ).prefetch_related(
                'tags', 'ingredients', 'recipe',
                'shopping_cart', 'favorite_recipe'
            )
        return Recipe.objects.annotate(
            is_favorited=Exists(FavoriteRecipe.objects.filter(
                user=self.request.user, recipe=OuterRef('id'))
            ),
            is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
                user=self.request.user, recipe=OuterRef('id'))
            )
        ).select_related(
            'author'
        ).prefetch_related(
            'tags', 'ingredients', 'recipe',
            'shopping_cart', 'favorite_recipe'
        )


# ! READY
class FavoriteRecipeDetail(generics.RetrieveDestroyAPIView):
    '''Избранный рецепт.'''
    serializer_class = SubscribeRecipeSerializer

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.favorite_recipe.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.favorite_recipe.recipe.remove(instance)


# ! READY
class IngredientDetail(generics.RetrieveAPIView):
    '''Получение ингредиента.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)


# ! READY
class IngredientList(generics.ListAPIView):
    '''Список ингридиентов.'''
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


# * Разобраться с методом POST
# ! NOTREADY
class ShoppingCartDetail(viewsets.ModelViewSet):
    '''Список покупок.'''
    serializer_class = SubscribeRecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.shopping_cart.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.shopping_cart.recipe.remove(instance)


# * Разобраться с методом POST
# ! NOTREADY
class SubscribeDetail(viewsets.ModelViewSet):
    '''Подписка на пользователя.'''
    serializer_class = SubscribeSerializer
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get_queryset(self):
        return self.request.user.follower.select_related(
            'following').prefetch_related(
                'following__recipe'
        ).annotate(
            recipes_count=Count('following__recipe'),
            is_subscribed=Value(True),
        )

    def get_object(self):
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        self.check_object_permissions(self.request, user)
        return user

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.id == instance.id:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.user.follower.filter(following=instance).exists():
            return Response(
                {'errors': 'Вы уже подписаны на этого пользователя.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subs = request.user.follower.create(following=instance)
        serializer = self.get_serializer(subs)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.follower.filter(
            following=instance).delete()


class SubscribeList(generics.ListAPIView):
    '''Список подписок.'''
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return self.request.user.follower.select_related(
            'following').prefetch_related(
                'following__recipe'
        ).annotate(
            recipes_count=Count('following__recipe'),
            is_subscribed=Value(True),
        )
