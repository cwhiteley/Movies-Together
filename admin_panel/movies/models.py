import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import UniqueConstraint
from django.utils.translation import gettext_lazy as _


class TimeStampedMixin(models.Model):
    created = models.DateTimeField(_("created"), auto_now_add=True)
    modified = models.DateTimeField(_("modified"), auto_now=True)

    class Meta:
        abstract = True


class UUIDMixin(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class Meta:
        abstract = True


class Genre(UUIDMixin, TimeStampedMixin):
    name = models.CharField(_("name"), max_length=255)
    description = models.TextField(_("description"), null=True)
    manged = True

    class Meta:
        db_table = 'movies_content"."genre'
        verbose_name = _("Genre")
        verbose_name_plural = _("Genres")

    def __str__(self):
        return self.name


class Person(UUIDMixin, TimeStampedMixin):
    class Gender(models.TextChoices):
        MALE = "male", _("male")
        FEMALE = "female", _("female")

    full_name = models.CharField(_("full_name"), max_length=255)
    gender = models.TextField(
        _("gender"), choices=Gender.choices, null=True, blank=True
    )
    # film_works = models.ManyToManyField(FilmWork, through="person_film_work")

    class Meta:
        db_table = 'movies_content"."person'
        verbose_name = _("Person")
        verbose_name_plural = _("Persons")
        indexes = [
            models.Index(fields=["full_name"], name="person_full_name_idx"),
        ]

    def __str__(self):
        return self.full_name


class FilmWork(UUIDMixin, TimeStampedMixin):
    certificate = models.CharField(_("certificate"), max_length=512, null=True)
    file_path = models.FileField(_("file"), blank=True, null=True, upload_to="movies/")
    title = models.CharField(_("title"), max_length=255)
    description = models.TextField(_("description"), null=True)
    creation_date = models.DateField(_("creation_date"), auto_now_add=True, blank=True)
    genres = models.ManyToManyField(Genre, through="GenreFilmwork")
    persons = models.ManyToManyField(Person, through="PersonFilmwork")
    rating = models.FloatField(
        _("rating"),
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )
    manged = True

    class Type(models.TextChoices):
        MOVIE = "Movie", _("Movie")
        TV_SHOW = "Tv_show", _("Tv_show")

    type = models.CharField(
        _("type"),
        max_length=25,
        choices=Type.choices,
    )

    class Meta:
        db_table = 'movies_content"."film_work'
        verbose_name = _("Movie")
        verbose_name_plural = _("Movies")
        indexes = [
            models.Index(fields=["creation_date"], name="film_work_creation_date_idx"),
        ]

    def __str__(self):
        return self.title


class GenreFilmwork(UUIDMixin):
    film_work = models.ForeignKey(
        FilmWork, on_delete=models.CASCADE, verbose_name=_("Film work")
    )
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, verbose_name=_("Genre"))
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'movies_content"."genre_film_work'
        verbose_name = _("Genre Filmwork")
        verbose_name_plural = _("Genre Filmworks")
        constraints = [
            UniqueConstraint(fields=["genre", "film_work"], name="film_work_genre_idx")
        ]


class PersonFilmwork(UUIDMixin):
    class Role(models.TextChoices):
        actor = "actor", _("Actor")
        director = "director", _("Director")
        writer = "writer", _("Writer")

    film_work = models.ForeignKey(
        FilmWork, on_delete=models.CASCADE, verbose_name=_("Film work")
    )
    person = models.ForeignKey(
        Person, on_delete=models.CASCADE, verbose_name=_("Person")
    )
    role = models.CharField(_("role"), choices=Role.choices, max_length=255)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'movies_content"."person_film_work'
        verbose_name = _("Person Filmwork")
        verbose_name_plural = _("Person Filmworks")
        constraints = [
            UniqueConstraint(
                fields=["person", "film_work", "role"], name="film_work_person_idx"
            )
        ]
