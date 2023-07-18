import csv
import datetime
import json

import pandas as pd
import tablib
from django.core.exceptions import ValidationError
from django.db import connection
from import_export.formats.base_formats import CSV, TablibFormat


class GEOJSON(TablibFormat):
    def get_title(self):
        return "geojson"

    def create_dataset(self, in_stream, **kwargs):
        """
        Create tablib.dataset from geojson.
        """

        if isinstance(in_stream, dict):
            data = in_stream
        else:
            data = json.load(tablib.utils.normalize_input(in_stream))

        try:
            crs = data["crs"]
        except:  # if not in Geojson -> default crs RD
            crs = {
                "type": "name",
                "properties": {"name": "urn:ogc:def:crs:EPSG::28992"},
            }

        df = data["features"]
        tmp = pd.DataFrame.from_records(df)
        df_properties = pd.DataFrame.from_records(tmp["properties"])

        # adds crs to geometry field -> necessary for function GEOSGeometry in resource.py
        # function GEOSGeometry has a bug at this moment (6-3-2023) when reading geojson geometry-field;
        # it defaults always to srid=4326 while we need srid=28992.
        # solution: add crs of the geojson to the geometry-field.
        tmp_list = []
        for feature in df:
            geometry = feature["geometry"]
            geometry["crs"] = crs
            tmp_list.append(str(geometry))

        df_properties["geometry"] = tmp_list

        _dset = tablib.Dataset()
        _dset.dict = df_properties.to_dict(orient="records")

        return _dset


class SCSV(CSV):
    def get_title(self):
        return "semicolon_csv"

    def create_dataset(self, in_stream, **kwargs):
        delimiter = csv.Sniffer().sniff(in_stream, delimiters=";,").delimiter
        if delimiter != ";":
            raise ValidationError(
                f"CSV format is using `{delimiter}` delimiter,"
                + " but it should be `;` delimiter"
            )
        kwargs["delimiter"] = delimiter
        kwargs["format"] = "csv"
        return tablib.import_set(in_stream, **kwargs)


# --------------------------------------


def truncate(model):
    """
    truncate db table and restart AutoField primary_key for import

    use as follows:
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        # truncate table before import when dry_run = False
        if not dry_run:
            truncate(modelobject)
    """

    raw_query = f"""
        TRUNCATE TABLE {model._meta.db_table} RESTART IDENTITY
        """

    with connection.cursor() as cursor:
        cursor.execute(raw_query, {})


def refresh_materialized(db_table: str):
    """
    refreshes materialized view db_table
    """

    raw_query = f"""
        REFRESH MATERIALIZED VIEW {db_table}
        """

    with connection.cursor() as cursor:
        cursor.execute(raw_query, {})


# -------------------------------------------


def convert_to_date(date: str = None, format: str = "%d/%m/%y %H:%M") -> datetime:
    """Convert string format to datetime"""

    try:
        _date = datetime.datetime.strptime(date, format)
    except:
        try:
            format = "%Y-%m-%d %H:%M:%S.%f"
            _date = datetime.datetime.strptime(date, format)
        except:
            raise ValueError(
                f"verkeerd datumformat voor {date}, gewenst format is '%d/%m/%y %H:%M' of '%Y-%m-%d %H:%M:%S.%f'"
            )

    return _date


def convert_to_time(in_time: str = None):
    """Convert string format to time"""

    if in_time == "":
        return None

    try:
        tlist = in_time.split(":")

        if len(tlist) == 2:
            tlist.append(0)  # aanvullen seconden

        _time = datetime.time(*map(int, tlist))
    except:
        raise ValueError(
            f"verkeerd datumformat voor {in_time}, gewenst format is H:M:S of H:M"
        )

    return _time


def convert_str(value: str, to: str = "float"):
    """Convert string-value to format 'to'"""
    if "float" == to:
        try:
            value = float(value)
        finally:
            return value
    else:
        return value


def remove_chars_from_value(value: str, chars: list) -> str:
    """Removes all characters in list chars from value"""
    v = value
    for c in chars:
        v = v.replace(c, "")
    return v
