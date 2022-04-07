from django.contrib import admin

from .models import Filmwork, Genre, GenreFilmwork, Person, PersonFilmWork


class GenreFilmworkInline(admin.TabularInline):
    model = GenreFilmwork


class PersonFilmworkInline(admin.TabularInline):
    model = PersonFilmWork


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_filter = ('name',)
    search_fields = ('description',)


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    inlines = (GenreFilmworkInline, PersonFilmworkInline)

    list_display = ('title', 'type', 'created_at', 'rating',)
    list_filter = ('type', 'rating')
    search_fields = ('title', 'description', 'id')


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
    list_display = ('full_name',)
    list_filter = ('created_at',)
    search_fields = ('full_name',)
