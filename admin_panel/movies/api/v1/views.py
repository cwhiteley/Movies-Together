from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.detail import BaseDetailView
from django.views.generic.list import BaseListView
from movies.models import FilmWork


class MoviesApiMixin:
    model = FilmWork
    http_method_names = ["get"]  # Список методов, которые реализует обработчик

    def get_person_aggregation(self, role: str):
        return ArrayAgg(
            "persons__full_name",
            filter=Q(persons__personfilmwork__role=role),
            distinct=True,
        )

    def get_queryset(self):
        return (
            FilmWork.objects.all()
            .prefetch_related("persons")
            .annotate(
                genre_list=ArrayAgg("genres__name", distinct=True),
                actors=self.get_person_aggregation("actor"),
                directors=self.get_person_aggregation("director"),
                writers=self.get_person_aggregation("writer"),
            )
        )

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context)


class MoviesListApi(MoviesApiMixin, BaseListView):
    def get_context_data(self, *, object_list=None, **kwargs):
        queryset = self.get_queryset()

        self.paginate_by = 50
        paginator, page, queryset, is_paginated = self.paginate_queryset(
            queryset, self.paginate_by
        )

        result = []
        for movie in page.object_list:
            result.append(
                {
                    "id": movie.id,
                    "title": movie.title,
                    "description": movie.description,
                    "creation_date": movie.creation_date,
                    "rating": movie.rating,
                    "type": movie.type,
                    "genres": movie.genre_list,
                    "actors": movie.actors,
                    "writers": movie.writers,
                    "directors": movie.directors,
                }
            )

        return {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "prev": page.previous_page_number() if page.has_previous() else None,
            "next": page.next_page_number() if page.has_next() else None,
            "results": result,
        }


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):
    def get_context_data(self, **kwargs):
        return {
            "id": self.object.id,
            "title": self.object.title,
            "description": self.object.description,
            "creation_date": self.object.creation_date,
            "rating": self.object.rating,
            "type": self.object.type,
            "genres": self.object.genre_list,
            "actors": self.object.actors,
            "writers": self.object.writers,
            "directors": self.object.directors,
        }
