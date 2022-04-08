from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db.models.aggregates import Count
from django.db.models.expressions import Exists, OuterRef, Value
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from recipes.models import (FavoriteRecipe, Ingredient, Recipe, ShoppingCart,
                            Tag)
from rest_framework import generics, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import action, api_view
from rest_framework.permissions import (AllowAny, IsAuthenticated,
                                        IsAuthenticatedOrReadOnly)
from rest_framework.response import Response

from api.filters import IngredientFilter, RecipeFilter
from api.permissions import IsAuthorOrAdminOrReadOnly

from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscribeRecipeSerializer, SubscribeSerializer,
                          TagsSerializer, TokenSerializer,
                          UserPasswordSerializer, UsersCreateSerializer,
                          UsersListSerializer)
from rest_framework.mixins import CreateModelMixin, ListModelMixin
User = get_user_model()


class UserList(UserViewSet, CreateModelMixin, ListModelMixin):
    permission_classes = (AllowAny,)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.annotate(is_subscribed=Value(False))
        return User.objects.annotate(
            is_subscribed=Exists(self.request.user.follower.filter(
                following=OuterRef('id')
            ))
        ).prefetch_related('follower', 'following')

    def perform_create(self, serializer):
        password = make_password(self.request.data['password'])
        serializer.save(password=password)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return UsersCreateSerializer
        return UsersListSerializer


class UserDetail(generics.RetrieveAPIView):
    serializer_class = UsersListSerializer
    permission_classes = (AllowAny,)

    def get_queryset(self):
        if not self.request.user.is_authenticated:
            return User.objects.annotate(is_subscribed=Value(False))
        return User.objects.annotate(
            is_subscribed=Exists(self.request.user.follower.filter(
                following=OuterRef('id')
            ))
        ).prefetch_related('follower', 'following')


@api_view(['GET'])
def about_me(request):
    serializer = UsersListSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
def set_password(request):
    serializer = UserPasswordSerializer(
        data=request.data, context={'request': request}
    )
    if serializer.is_valid():
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthToken(ObtainAuthToken):

    serializer_class = TokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {'auth_token': token.key}, status=status.HTTP_201_CREATED
        )


@api_view(['POST'])
def logout(request):
    token = get_object_or_404(Token, user=request.user)
    token.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)


class TagDetail(generics.RetrieveAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)


class TagList(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagsSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientList(generics.ListAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    permission_classes = (AllowAny,)
    pagination_class = None


class IngredientDetail(generics.RetrieveAPIView):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)


class RecipeList(generics.ListCreateAPIView):
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


class RecipeDetail(generics.RetrieveUpdateDestroyAPIView):
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
