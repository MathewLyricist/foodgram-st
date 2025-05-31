from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class UserForeignKey(models.ForeignKey):
    """
    FK-поле для пользователей.

    По-умолчанию:
    - to=User
    - on_delete=CASCADE
    """

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('on_delete', models.CASCADE)
        kwargs.setdefault('to', User)
        return super().__init__(*args, **kwargs)
