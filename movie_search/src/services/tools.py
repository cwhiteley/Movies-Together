import functools
from typing import Any

from db.elastic import Query, QueryTree
from elasticsearch import NotFoundError


def make_elastic_params(
    query_key: str,
    page_num: int = 1,
    page_size: int = 9999,
    sort_by: str | None = None,
    query: str | None = None,
    filter_film_by_genre_id: str | None = None,
    filter_film_by_person_id: str | None = None,
) -> dict[str, Any]:
    """Return params for elastic search"""

    parameters = {
        "from_": (page_num - 1) * page_size,
        "size": page_size,
    }
    if sort_by:
        sort_order = "desc" if sort_by[0] == "-" else "asc"
        sort_key = sort_by[1:] if sort_by[0] == "-" else sort_by
        parameters["sort"] = {sort_key: sort_order}

    tree = QueryTree()
    if query:
        tree.add(Query("match", {query_key: {"query": query, "fuzziness": "auto"}}))

    if filter_film_by_genre_id:
        subtree = QueryTree()
        subtree.add(Query("term", {"genre.id": filter_film_by_genre_id}))
        tree.add_nested("genre", subtree, "filter")

    if filter_film_by_person_id:
        actors = QueryTree()
        writers = QueryTree()
        directors = QueryTree()

        actors.add(Query("term", {"actors.id": filter_film_by_person_id}))
        writers.add(Query("term", {"writers.id": filter_film_by_person_id}))
        directors.add(Query("term", {"directors.id": filter_film_by_person_id}))

        tree.add_nested("actors", actors, "should")
        tree.add_nested("writers", writers, "should")
        tree.add_nested("directors", directors, "should")
    return {**parameters, "query": tree.dict()}


def not_found_error(fn):
    """Return None if exception NotFoundError"""

    @functools.wraps(fn)
    async def decorated(*args, **kwargs):
        try:
            return await fn(*args, **kwargs)
        except NotFoundError:
            return None

    return decorated
