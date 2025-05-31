### Валидационные ограничения ###
MIN_INTEGER_VALUE = 1
MAX_INTEGER_VALUE = 32_000

### Шаблоны сообщений об ошибках ###
TEMPLATE_MESSAGE_MINIMUM_ONE_ERROR = 'Должен быть хотя бы один {field_name}.'
TEMPLATE_MESSAGE_UNIQUE_ERROR = '{field_name} не должны повторяться.'

### Готовые сообщения об ошибках ###
REPEAT_ADDED_FAVORITE_ERROR = 'Нельзя повторно добавить рецепт в избранные.'
REPEAT_ADDED_SHOPPING_CART_ERROR = 'Нельзя повторно добавить рецепт в корзину.'
MIN_COOKING_TIME_ERROR = f'Время не может быть меньше {MIN_INTEGER_VALUE} минуты.'
MAX_COOKING_TIME_ERROR = f'Время не может быть меньше {MAX_INTEGER_VALUE} минуты.'
MIN_INGREDIENT_AMOUNT_ERROR = f'Количество должно быть равно {MIN_INTEGER_VALUE} или больше.'
MAX_INGREDIENT_AMOUNT_ERROR = f'Количество должно быть равно {MAX_INTEGER_VALUE} или больше.'
USER_EMAIL_ERROR = 'Данный электронный адрес уже используется.'
USER_USERNAME_ERROR = 'Пользователь с таким ником уже существует.'
SUPERUSER_STAFF_ERROR = 'Суперпользователь должен иметь is_staff=True.'

### Префиксы схем ###
COOKBOOK = 'cookbook'
AUTH = 'auth'

### Ограничения длины текстовых полей ###
LENGTH_CHARFIELD_32 = 32
LENGTH_CHARFIELD_64 = 64
LENGTH_CHARFIELD_128 = 128
LENGTH_CHARFIELD_150 = 150
LENGTH_CHARFIELD_256 = 256

### Пути и URL ###
RECIPE_IMAGE_PATH = 'recipes/images/'
RECIPE_DETAIL_URL = '/api/recipes/{pk}/'
FRONTEND_DETAIL_URL = '/recipes/{pk}/'
USER_AVATAR_PATH = 'users/'

### Прочие настройки ###
MAX_LENGTH_SHORT_LINK = 6