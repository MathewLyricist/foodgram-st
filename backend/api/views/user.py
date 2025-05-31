from djoser import views as djoser_views
from rest_framework import response, status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request

from api.permissions import ReadOnly
from api.serializers import AvatarSerializer, UserSerializer
from api.views.subscription import SubscriptionMixin
from users.models import User


class UserViewSet(djoser_views.UserViewSet, SubscriptionMixin):
    """Вьюсет для работы с пользователями."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = PageNumberPagination
    pagination_class.page_size_query_param = 'limit'
    permission_classes = [IsAuthenticated | ReadOnly]

    @action(
        ['GET', 'PUT', 'PATCH', 'DELETE'],
        detail=False,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request, *args, **kwargs):
        """Обработчик для работы с данными текущего пользователя.

        Поддерживает:
        - Получение данных (GET)
        - Обновление данных (PUT/PATCH)
        - Удаление аккаунта (DELETE)
        """
        return super().me(request, *args, **kwargs)

    @action(
        ['PUT'],
        detail=False,
        url_path='me/avatar',
        name='set_avatar',
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request: Request, *args, **kwargs):
        """Обновляет аватар текущего пользователя."""
        if 'avatar' not in request.data:
            return response.Response(
                {'avatar': 'Отсутствует изображение'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AvatarSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        avatar_data = serializer.validated_data.get('avatar')
        request.user.avatar = avatar_data
        request.user.save()

        image_url = request.build_absolute_uri(
            f'/media/users/{avatar_data.name}'
        )
        return response.Response(
            {'avatar': str(image_url)}, status=status.HTTP_200_OK
        )

    @avatar.mapping.delete
    def delete_avatar(self, request: Request, *args, **kwargs):
        """Удаляет аватар текущего пользователя."""
        user = self.request.user
        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
        return response.Response(status=status.HTTP_204_NO_CONTENT)