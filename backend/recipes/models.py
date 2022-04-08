from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipe',
        verbose_name='Автор рецепта')
    name = models.CharField(
        'Название рецепта',
        max_length=255)
    image = models.ImageField(
        'Изображение рецепта',
        upload_to='images_recipe/')
    text = models.TextField(
        'Текст рецепта')
    cooking_time = models.BigIntegerField(
        'Время приготовления рецепта')
    ingredients = models.ManyToManyField(
        'Ingredient',
        through='RecipeIngredient')
    tags = models.ManyToManyField(
        'Tag',
        through='RecipeTag')
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True)

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return f'Пользователь {self.author.email} добавил рецепт {self.name}'


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipe')
    ingredient = models.ForeignKey(
        'Ingredient',
        on_delete=models.CASCADE,
        related_name='ingredient')
    amount = models.BigIntegerField(
        'Количество ингредиента')

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique ingredient')]


class RecipeTag(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE)
    tag = models.ForeignKey(
        'Tag',
        on_delete=models.CASCADE)


class Tag(models.Model):
    name = models.CharField(
        'Имя тэга',
        max_length=200,
        unique=True)
    color = models.CharField(
        'Цвет тэга (#EA692F)',
        max_length=7,
        unique=True)
    slug = models.SlugField(
        'Слаг тэга',
        max_length=200,
        unique=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return f'Тэг {self.name} добавлен'


class Ingredient(models.Model):
    name = models.CharField(
        'Название ингредиента',
        max_length=200)
    measurement_unit = models.CharField(
        'Единица измерения ингредиента',
        max_length=200)

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'Ингридиент {self.name} ({self.measurement_unit}) создан.'


class Subscribe(models.Model):
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Пользователь')
    created = models.DateTimeField(
        'Дата подписки',
        auto_now_add=True)

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['follower', 'following'],
                name='unique subs')]

    def __str__(self):
        return (
            f'Пользователь {self.follower} '
            f'подписался на {self.following}')


class FavoriteRecipe(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Пользователь')
    recipe = models.ManyToManyField(
        Recipe,
        related_name='favorite_recipe',
        verbose_name='Избранный рецепт')

    class Meta:
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        list_ = [_.name for _ in self.recipe.all()]
        return f'Пользователь {self.user} добавил {list_} в избранные.'

    @receiver(post_save, sender=User)
    def create_favorite_recipe(
            sender, instance, created, **kwargs):
        if created:
            return FavoriteRecipe.objects.create(user=instance)


class ShoppingCart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь')
    recipe = models.ManyToManyField(
        Recipe,
        related_name='shopping_cart',
        verbose_name='Рецепт в корзине покупок')

    class Meta:
        verbose_name = 'Корзина с рецептом'
        verbose_name_plural = 'Корзина с рецептами'

    def __str__(self):
        list_ = [_.name for _ in self.recipe.all()]
        return f'Пользователь {self.user} добавил {list_} в корзину.'

    @receiver(post_save, sender=User)
    def create_shopping_cart(
            sender, instance, created, **kwargs):
        if created:
            return ShoppingCart.objects.create(user=instance)
