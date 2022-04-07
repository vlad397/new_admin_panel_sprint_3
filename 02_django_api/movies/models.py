import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created_at = models.DateTimeField(_('created_at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated_at'), auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_('name'), max_length=255)
    description = models.TextField(_('description'), blank=True)

    class Meta:
        db_table = "content\".\"genre"
        verbose_name = 'жанр'
        verbose_name_plural = 'жанры'

    def __str__(self):
        return self.name


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    genre = models.ForeignKey('Genre', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"genre_film_work"
        constraints = [models.UniqueConstraint(fields=['film_work', 'genre'],
                       name='unique_film_work_genre')]

    def __str__(self):
        return '{0} - {1}'.format(self.film_work, self.genre)


class Person(UUIDMixin, TimeStampedMixin):
    full_name = models.CharField('full_name', max_length=255)

    class Meta:
        db_table = "content\".\"person"
        verbose_name = 'персона'
        verbose_name_plural = 'персоны'

    def __str__(self):
        return self.full_name


class PersonFilmWork(UUIDMixin, models.Model):
    film_work = models.ForeignKey('Filmwork', on_delete=models.CASCADE)
    person = models.ForeignKey('Person', on_delete=models.CASCADE)

    class Role(models.TextChoices):
        ACTOR = 'actor', _('actor')
        WRITER = 'writer', _('writer')
        DIRECTOR = 'direrctor', _('director')
    role = models.CharField(
        _('role'),
        max_length=10,
        choices=Role.choices,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "content\".\"person_film_work"
        constraints = [models.UniqueConstraint(fields=['film_work', 'person',
                                                       'role'],
                       name='unique_person_and_role_for_film_work')]

    def __str__(self):
        return '{0} - {1}'.format(self.film_work, self.person)


class Filmwork(UUIDMixin, TimeStampedMixin):
    title = models.CharField(_('title'), max_length=255)
    description = models.TextField(_('description'), blank=True, null=True)
    creation_date = models.DateField()
    file_path = models.TextField(_('file_path'), blank=True)
    rating = models.FloatField(
        _('rating'), blank=True, null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )

    class Type(models.TextChoices):
        MOVIE = 'MV', _('Movie')
        TV_SHOW = 'TV', _('TV_show')

    type = models.CharField(
        _('type'),
        max_length=5,
        choices=Type.choices,
        default=Type.MOVIE,
    )
    genres = models.ManyToManyField(Genre, through='GenreFilmwork')
    persons = models.ManyToManyField(Person, through='PersonFilmWork')

    class Meta:
        db_table = "content\".\"film_work"
        verbose_name = 'кинопроизведение'
        verbose_name_plural = 'кинопроизведения'

    def __str__(self):
        return self.title
