from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from api.filters import RecipeFilter
from api.permissions import IsAuthorOrReadOnly, ReadOnly
from api.serializers import RecipeChangeSerializer, RecipeGetSerializer
from api.views.recipe_favorite import RecipeFavoriteMixin
from api.views.shopping_cart import ShoppingCartMixin
from recipes.models import Recipe


class RecipeViewSet(
    viewsets.ModelViewSet,
    RecipeFavoriteMixin,
    ShoppingCartMixin
):
    """Вьюсет для работы с рецептами и связанными действиями."""

    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    serializer_class = RecipeChangeSerializer
    ordering = ['-id']

    def get_permissions(self):
        """Определяет права доступа в зависимости от действия."""
        if (
            self.action == 'download_shopping_cart'
            or self.request.method == 'POST'
        ):
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    def get_serializer_class(self):
        """Выбирает сериализатор в зависимости от типа запроса."""
        if self.action in ('list', 'retrieve'):
            return RecipeGetSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeChangeSerializer
        return super().get_serializer_class()

    def perform_create(self, serializer: Serializer):
        """Создает рецепт с указанием автора."""
        serializer.is_valid(raise_exception=True)
        serializer.save(author=self.request.user)

    def partial_update(self, request: Request, *args, **kwargs):
        """Частичное обновление рецепта с валидацией."""
        instance = self.get_object()
        data = request.data.copy()

        serializer: Serializer = self.get_serializer(
            instance,
            data=data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        super().perform_update(serializer)
        return Response(serializer.data)

    @action(detail=True, methods=['GET'], url_path='get-link')
    def get_short_link(self, request: Request, pk: int):
        """Генерирует короткую ссылку для рецепта."""
        try:
            recipe: Recipe = self.get_object()
        except Recipe.DoesNotExist:
            return Response(
                {'message': 'Не существует такой записи'},
                status=status.HTTP_404_NOT_FOUND
            )

        scheme = request.scheme
        host = request.get_host()
        domain = f'{scheme}://{host}'
        return Response(
            {'short-link': f'{domain}/s/{recipe.short_link}'},
            status=status.HTTP_200_OK
        )


class RecipeRedirectView(APIView):
    """Обработчик редиректа с короткой ссылки на полный адрес рецепта."""

    permission_classes = [ReadOnly]

    def get(self, request: Request, short_link: str):
        recipe = get_object_or_404(Recipe, short_link=short_link)
        return redirect(recipe.get_frontend_absolute_url())