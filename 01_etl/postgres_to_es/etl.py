import datetime as dt
import logging
import os
import os.path
from contextlib import contextmanager
from time import sleep

import backoff
import elasticsearch
import psycopg2
import redis
from dotenv import load_dotenv
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor

load_dotenv()


@backoff.on_exception(backoff.expo, BaseException)
def etl(pg_conn: _connection, es: elasticsearch.client.Elasticsearch) -> None:
    """Считывание состояния последнего обновления в хранилище
       Детектирование более новых записей в БД относительно состояния
       Обновление соответствующих записей в ElasticSearch"""
    logging.info('Начало etl')

    # Подключение к хранилищу, получение состояния
    r = redis.Redis(host=os.environ.get('REDIS_HOST'),
                    port=os.environ.get('REDIS_PORT'))
    if not r.exists('film_work') == 1:
        r.set(name='film_work', value=dt.datetime.min.isoformat())
    state = dt.datetime.fromisoformat(r.get('film_work').decode("utf-8"))

    # Подключение к БД, обнаружение обновленных относительно состояния записей
    pg_cursor = pg_conn.cursor()
    pg_cursor.execute("SELECT * FROM content.film_work WHERE "
                      "updated_at > '{0}'".format(state))
    pg_objects = pg_cursor.fetchall()

    if pg_objects:
        for data in pg_objects:
            id = data[2]
            title = data[3]
            description = data[4]
            rating = data[7]

            # Запрос на получение всех участвующих в определенном фильме людей
            query_roles = (
                "SELECT "
                "pfw.role, "
                "p.id, "
                "p.full_name "
                "FROM content.film_work fw "
                "LEFT JOIN content.person_film_work pfw ON "
                "pfw.film_work_id = fw.id "
                "LEFT JOIN content.person p ON p.id = pfw.person_id "
                "WHERE film_work_id='{0}' "
                "ORDER BY pfw.role;".format(id))

            actors_names = []
            writers_names = []
            directors = []
            actors = []
            writers = []

            pg_cursor.execute(query_roles)
            for person in pg_cursor.fetchall():
                if person[0] == 'actor':
                    actors_names.append(person[2])
                    actors.append({'id': person[1], 'name': person[2]})
                elif person[0] == 'writer':
                    writers_names.append(person[2])
                    writers.append({'id': person[1], 'name': person[2]})
                elif person[0] == 'director':
                    directors.append(person[2])

            # Запрос на получение всех жанров определенного фильма
            query_genres = (
                "SELECT "
                "g.name "
                "FROM content.film_work fw "
                "LEFT JOIN content.genre_film_work gfw ON "
                "gfw.film_work_id = fw.id "
                "LEFT JOIN content.genre g ON g.id = gfw.genre_id "
                "WHERE film_work_id='{0}';".format(id))

            genres = []

            pg_cursor.execute(query_genres)
            for genre in pg_cursor.fetchall():
                genres.append(genre[0])

            # Подготовка и отправка объекта в ElasticSearch
            object = {
                'id': id,
                'imdb_rating': rating,
                'genre': genres,
                'title': title,
                'description': description,
                'director': directors,
                'actors_names': actors_names,
                'writers_names': writers_names,
                'actors': actors,
                'writers': writers
            }

            es.index(index='movies', id=object['id'], body=object)
            logging.info(
                'Изменения для <{0}> перенесены в ElasticSearch'.format(
                    object['title']))
    else:
        logging.info('Изменений не обнаружено')

    # Обновление состояния в хранилище
    r.set(name='film_work', value=dt.datetime.utcnow().isoformat())


@backoff.on_exception(backoff.expo, BaseException)
def try_connect(dsl: dict, es_dsl: dict) -> None:
    """Подключение к PostgreSQL и ElasticSearch"""
    @contextmanager
    def pg_context(dsl: dict):
        pg_conn = psycopg2.connect(**dsl, cursor_factory=DictCursor)
        try:
            yield pg_conn
        finally:
            pg_conn.close()

    es = elasticsearch.Elasticsearch([es_dsl])
    logging.info('Подключение к ElasicSearch выполнено')

    with pg_context(dsl) as pg_conn, pg_conn:
        logging.info('Подключение к БД выполнено')
        etl(pg_conn, es)


if __name__ == '__main__':
    logging.basicConfig(
        level=logging.DEBUG,
        filename='main.log',
        format='%(asctime)s, %(levelname)s, %(name)s, %(message)s',
        encoding='utf-8'
    )

    dsl = {
        'dbname': os.environ.get('POSTGRES_DB'),
        'user': os.environ.get('POSTGRES_USER'),
        'password': os.environ.get('POSTGRES_PASSWORD'),
        'host': os.environ.get('DB_HOST', '127.0.0.1'),
        'port': os.environ.get('DB_PORT', 5432)
    }

    es_dsl = {
        'host': os.environ.get('ES_HOST', 'localhost'),
        'port': os.environ.get('ES_PORT', 9200)
        }

    while True:
        try_connect(dsl, es_dsl)
        sleep(10)
