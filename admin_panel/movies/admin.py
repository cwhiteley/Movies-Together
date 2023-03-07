from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import FilmWork, Genre, GenreFilmwork, Person, PersonFilmwork


class GenreFilmWorkInline(admin.TabularInline):
    verbose_name = _("Genre")
    verbose_name_plural = _("Genres")
    model = GenreFilmwork
    autocomplete_fields = ("genre",)


class PersonFilmworkInline(admin.TabularInline):
    verbose_name = _("Person")
    verbose_name_plural = _("Persons")
    model = PersonFilmwork
    autocomplete_fields = ("person",)


@admin.register(FilmWork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmWorkInline, PersonFilmworkInline)
    # Отображение полей в списке
    list_display = (
        "title",
        "type",
        "creation_date",
        "get_genres",
        "rating",
    )
    # Фильтрация в списке
    list_filter = ("type",)
    # Поиск по полям
    search_fields = (
        "title",
        "description",
        "id",
    )
    list_prefetch_related = ("genres",)

    def get_queryset(self, request):
        queryset = (
            super().get_queryset(request).prefetch_related(*self.list_prefetch_related)
        )
        return queryset

    def get_genres(self, obj):
        return ", ".join([genre.name for genre in obj.genres.all()])

    get_genres.short_description = "Жанры фильма"


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = (
        "name",
        "id",
    )


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    inlines = (PersonFilmworkInline,)
    list_display = (
        "full_name",
        "gender",
    )
    list_filter = ("gender",)
    search_fields = (
        "full_name",
        "id",
    )
