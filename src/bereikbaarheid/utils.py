from typing import Union

from django.db import connection


def convert_to_bool(value: Union[str, int]) -> bool:
    return value in ["true", 1, "y", "yes", "True"]


def django_query_db(raw_query_string: str, parameters: dict, single=False) -> Union[list[tuple], tuple]:
    """
    Query the database with a raw query
    :param raw_query_string:
    :param parameters:
    :param single:
    :return:
    """
    with connection.cursor() as cursor:
        cursor.execute(raw_query_string, parameters)
        if single:
            return cursor.fetchone()
        else:
            return cursor.fetchall()
