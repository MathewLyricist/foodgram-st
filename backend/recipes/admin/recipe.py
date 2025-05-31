from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from recipes.models.recipe import Recipe
from recipes.models.recipe_favorite import RecipeFavorite
from recipes.models.recipe_ingredients import RecipeIngredients


class RecipeIngredientInline(admin.TabularInline):
    """Админ-инлайн для управления ингредиентами в рецепте."""

    model = RecipeIngredients
    autocomplete_fields = ['ingredient']
    extra = 1
    min_num = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ-панель для управления рецептами."""

    # Отображение в списке
    list_display = (
        'name',
        'author_link',
        'pub_date',
        'favorites_count',
    )
    # Поля для поиска
    search_fields = (
        'name',
        'author__username',
        'author__email',
        'author__first_name',
        'author__last_name'
    )
    autocomplete_fields = ('author',)
    readonly_fields = ('short_link', 'pub_date')
    ordering = ('-pub_date',)

    # Группировка полей в форме редактирования
    fieldsets = (
        (None, {
            'fields': ('name', 'author', 'image', 'text', 'cooking_time')
        }),
        ('Дополнительно', {
            'fields': ('short_link', 'pub_date'),
            'classes': ('collapse',)
        }),
    )

    # Инлайн-модели
    inlines = (RecipeIngredientInline,)

    def author_link(self, obj):
        """Ссылка на автора рецепта в админке."""
        url = reverse('admin:users_user_change', args=[obj.author.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            f"{obj.author.get_full_name()} ({obj.author.email})"
        )

    author_link.short_description = 'Автор'
    author_link.admin_order_field = 'author'

    def favorites_count(self, obj):
        """Количество добавлений рецепта в избранное."""
        return obj.favorites.count()

    favorites_count.short_description = 'В избранном'
    favorites_count.admin_order_field = 'favorites_count'

    def get_queryset(self, request):
        """Оптимизация запросов с помощью select_related и annotate."""
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('author')
        return queryset