from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.aggregates import Count
from django.db.models.expressions import Exists, OuterRef, Value
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from rest_framework import generics, status
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin, ListModelMixin,)
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrAdminOrReadOnly

from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscribeRecipeSerializer, SubscribeSerializer,
                          TagsSerializer, UserPasswordSerializer,
                          UsersCreateSerializer, UsersListSerializer)

User = get_user_model()


class UserList(
                UserViewSet,
                CreateModelMixin,
                ListModelMixin):
    """
    Пользователи...
    """
    permission_classes = (AllowAny,)

    def get_queryset(self):
        return User.objects.annotate(
            is_subscribed=Exists(
                self.request.user.follower.filter(
                    following=OuterRef('id'))
            )).prefetch_related(
                'follower', 'following'
        ) if self.request.user.is_authenticated else User.objects.annotate(
            is_subscribed=Value(False))

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UsersCreateSerializer
        return UsersListSerializer

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[IsAuthorOrAdminOrReadOnly])
    def about_me(self):
        """
        Информация о текущем пользователе.
        """
        serializer = UsersListSerializer(self.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthorOrAdminOrReadOnly])
    def set_password(self):
        serializer = UserPasswordSerializer(
            data=self.request.data, context={'request': self.request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthorOrAdminOrReadOnly])
    def logout(self):
        token = get_object_or_404(Token, user=self.request.user)
        token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TagsViewSet(ReadOnlyModelViewSet, ListModelMixin):
    """
    Список тэгов.
    """
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientsViewSet(ReadOnlyModelViewSet, ListModelMixin):
    """
    Список ингредиентов.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipesViewSet(
                UserViewSet,
                CreateModelMixin,
                ListModelMixin):
    """
    Список рецептов.
    """
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
                'shopping_cart', 'favorite_recipe')
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


# class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
#     serializer_class = RecipeSerializer
#     permission_classes = (IsAuthorOrAdminOrReadOnly,)

#     def get_queryset(self):
#         if not self.request.user.is_authenticated:
#             return Recipe.objects.annotate(
#                 is_in_shopping_cart=Value(False),
#                 is_favorited=Value(False),
#             ).select_related(
#                 'author'
#             ).prefetch_related(
#                 'tags', 'ingredients', 'recipe',
#                 'shopping_cart', 'favorite_recipe'
#             )
#         return Recipe.objects.annotate(
#             is_favorited=Exists(FavoriteRecipe.objects.filter(
#                 user=self.request.user, recipe=OuterRef('id'))
#             ),
#             is_in_shopping_cart=Exists(ShoppingCart.objects.filter(
#                 user=self.request.user, recipe=OuterRef('id'))
#             )
#         ).select_related(
#             'author'
#         ).prefetch_related(
#             'tags', 'ingredients', 'recipe',
#             'shopping_cart', 'favorite_recipe'
#         )


class SubscribeList(generics.ListAPIView):
    serializer_class = SubscribeSerializer

    def get_queryset(self):
        return self.request.user.follower.select_related(
            'following').prefetch_related(
                'following__recipe'
        ).annotate(
            recipes_count=Count('following__recipe'),
            is_subscribed=Value(True),
        )


class SubscribeDetail(
        generics.ListCreateAPIView,
        generics.DestroyAPIView):
    serializer_class = SubscribeSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return self.request.user.follower.select_related(
            'following').prefetch_related(
                'following__recipe'
        ).annotate(
            recipes_count=Count('following__recipe'),
            is_subscribed=Value(True),
        )

    def get_object(self):
        user = get_object_or_404(
            User,
            id=self.kwargs['user_id'])
        self.check_object_permissions(self.request, user)
        return user

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        user_ = request.user
        if user_.id == instance.id:
            return Response(
                {'errors': 'На себя не подписаться.'},
                status=status.HTTP_400_BAD_REQUEST)
        if user_.follower.filter(following=instance).exists():
            return Response(
                {'error': 'Уже подписан.'},
                status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(
            user_.follower.create(following=instance))
        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.follower.filter(
            following=instance).delete()


class FavoriteRecipeDetail(
        generics.CreateAPIView,
        generics.RetrieveDestroyAPIView):
    queryset = Recipe.objects.all()
    serializer_class = SubscribeRecipeSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.favorite_recipe.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.favorite_recipe.recipe.remove(instance)


class ShoppingCartDetail(
        generics.ListCreateAPIView,
        generics.RetrieveDestroyAPIView,):

    queryset = Recipe.objects.all()
    serializer_class = SubscribeRecipeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        recipe_id = self.kwargs['recipe_id']
        recipe = get_object_or_404(Recipe, id=recipe_id)
        self.check_object_permissions(self.request, recipe)
        return recipe

    def create(self, request, *args, **kwargs):
        instance = self.get_object()
        request.user.shopping_cart.recipe.add(instance)
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        self.request.user.shopping_cart.recipe.remove(instance)
