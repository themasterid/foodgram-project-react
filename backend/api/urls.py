from django.urls import path

from .utils import download_shopping_cart
from .views import (AuthToken, FavoriteRecipeDetail, IngredientDetail,
                    IngredientList, GetUpdateDeleteRecipe, RecipeList,
                    RegisterAndUserList, ShoppingCartDetail, SubscribeDetail,
                    SubscribeList, TagDetail, TagList, UserDetail, about_me,
                    logout, set_password)

app_name = 'api'

urlpatterns = [
    path('users/', RegisterAndUserList.as_view(), name='user_list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user_detail'),
    path('users/me/', about_me, name='about_me'),
    path('users/set_password/', set_password, name='set_password'),
    path('auth/token/login/', AuthToken.as_view(), name='login'),
    path('auth/token/logout/', logout, name='logout'),

    path(
        'tags/',
        TagList.as_view(),
        name='tag_list'),
    path(
        'tags/<int:pk>/',
        TagDetail.as_view(),
        name='tag_detail'),


    path(
        'users/subscriptions/',
        SubscribeList.as_view(),
        name='subscribe_list'),
    path(
        'users/<int:user_id>/subscribe/',
        SubscribeDetail.as_view({'get': 'list'}),
        name='subscribe'),

    path('recipes/', RecipeList.as_view(), name='recipe_list'),
    path(
        'recipes/<int:pk>/',
        GetUpdateDeleteRecipe.as_view(),
        name='recipe_detail'),
    path(
        'recipes/<int:recipe_id>/favorite/',
        FavoriteRecipeDetail.as_view(),
        name='favorite_recipe'),
    path(
        'recipes/<int:recipe_id>/shopping_cart/',
        ShoppingCartDetail.as_view({'get': 'list'}),
        name='shopping_cart'),
    path(
        'recipes/download_shopping_cart/',
        download_shopping_cart,
        name='download_shopping_cart'),

    path(
        'ingredients/',
        IngredientList.as_view(),
        name='ingredient_list'),
    path(
        'ingredients/<int:pk>/',
        IngredientDetail.as_view(),
        name='ingredient_detail'),
]
