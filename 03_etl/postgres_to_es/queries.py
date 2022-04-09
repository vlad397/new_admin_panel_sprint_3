from datetime import datetime


def make_query(where_block: str) -> str:
    # Получение всех фильмов по приходящему WHERE
    query_fw = (
    "SELECT "
        "fw.id, "
        "fw.rating, "
        "fw.title, "
        "fw.description, "
        "ARRAY_AGG(DISTINCT g.name) AS genres, "
        "ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'actor') AS actors_names, "
        "ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'writer') AS writers_names, "
        "ARRAY_AGG(DISTINCT p.full_name) FILTER (WHERE pfw.role = 'director') AS directors, "
        "ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'actor') AS actors, "
        "ARRAY_AGG(DISTINCT jsonb_build_object('id', p.id, 'name', p.full_name)) FILTER (WHERE pfw.role = 'writer') AS writers "
    "FROM content.film_work fw "
        "LEFT JOIN content.person_film_work pfw ON pfw.film_work_id = fw.id "
        "LEFT JOIN content.person p ON p.id = pfw.person_id "
        "LEFT JOIN content.genre_film_work gfw ON gfw.film_work_id = fw.id "
        "LEFT JOIN content.genre g ON g.id = gfw.genre_id "
    "{0}"
    "GROUP BY fw.id".format(where_block))

    return query_fw


def make_prequery(index: str, state: datetime) -> str:
    # Поулчение всех фильмов, связанных с обновленным жанром
    query_g = (
    "SELECT "
        "fw.id "
    "FROM content.genre_film_work gfw "
        "LEFT JOIN content.film_work fw ON fw.id = gfw.film_work_id "
        "LEFT JOIN content.genre g ON g.id = gfw.genre_id "
    "WHERE g.updated_at > '{0}' "
    "GROUP BY fw.id".format(state))

    # Поулчение всех фильмов, связанных с обновленным человеком
    query_p = (
    "SELECT "
        "fw.id "
    "FROM content.person_film_work pfw "
        "LEFT JOIN content.film_work fw ON fw.id = pfw.film_work_id "
        "LEFT JOIN content.person p ON p.id = pfw.person_id "
    "WHERE p.updated_at > '{0}' "
    "GROUP BY fw.id".format(state))

    if index == 'genre':
        return query_g
    if index == 'person':
        return query_p
