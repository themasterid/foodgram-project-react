# from django.urls import path

# from .utils import download_shopping_cart
# from .views import (AuthToken, FavoriteRecipeDetail, IngredientDetail,
#                     IngredientList, RecipeDetail, RecipeList,
#                     ShoppingCartDetail, SubscribeDetail, SubscribeList,
#                     TagDetail, TagList, UserDetail, UserList, about_me, logout,
#                     set_password)

# app_name = 'api'

# urlpatterns = [
#     path('users/', UserList.as_view(), name='user_list'),
#     path('users/<int:pk>/', UserDetail.as_view(), name='user_detail'),
#     path('users/set_password/', set_password, name='set_password'),
#     path('users/me/', about_me, name='about_me'),
#     path('users/subscriptions/', SubscribeList.as_view(),
#          name='subscribe_list'),
#     path('users/<int:user_id>/subscribe/', SubscribeDetail.as_view(),
#          name='subscribe'),
#     path('auth/token/login/', AuthToken.as_view(), name='login'),
#     path('auth/token/logout/', logout, name='logout'),
#     path('tags/', TagList.as_view(), name='tag_list'),
#     path('tags/<int:pk>/', TagDetail.as_view(), name='tag_detail'),

#     path('ingredients/', IngredientList.as_view(), name='ingredient_list'),
#     path('ingredients/<int:pk>/', IngredientDetail.as_view(),
#          name='ingredient_detail'),

#     path('recipes/', RecipeList.as_view(), name='recipe_list'),
#     path('recipes/<int:pk>/', RecipeDetail.as_view(), name='recipe_detail'),
#     path('recipes/<int:recipe_id>/favorite/', FavoriteRecipeDetail.as_view(),
#          name='favorite_recipe'),
#     path('recipes/<int:recipe_id>/shopping_cart/',
#          ShoppingCartDetail.as_view(),
#          name='shopping_cart'),
#     path('recipes/download_shopping_cart/', download_shopping_cart,
#          name='download_shopping_cart'),
# ]

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import UserList, about_me
# , IngredientsViewSet, RecipeViewSet,
#                        TagsViewSet)

app_name = 'api'

router = DefaultRouter()
# router.register('tags', TagsViewSet)
# router.register('ingredients', IngredientsViewSet)
# router.register('recipes', RecipeViewSet)
router.register('users/', UserList)

urlpatterns = [
    path('', include(router.urls)),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]
