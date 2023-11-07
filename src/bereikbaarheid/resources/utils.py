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

        # json-field "geometry" is saved in tablib-field "geom"
        df_properties["geom"] = tmp_list

        _dset = tablib.Dataset()
        _dset.dict = df_properties.to_dict(orient="records")

        return _dset


class SCSV(CSV):
    def get_title(self):
        return "semicolon_csv"

    def create_dataset(self, in_stream, **kwargs):
        if isinstance(in_stream, bytes) and self.encoding:
            in_stream = in_stream.decode(self.encoding)

        delimiter = csv.Sniffer().sniff(in_stream, delimiters=";,").delimiter

        if delimiter != ";":
            raise ValidationError(
                f"file is using `{delimiter}` delimiter,"
                + " but semicolon_csv format is with `;` delimiter"
            )
        kwargs["delimiter"] = delimiter
        kwargs["format"] = "csv"
        return tablib.import_set(in_stream, **kwargs)

    def export_data(self, dataset, **kwargs):
        """overwrite export_data from import_export.formats.base_formats for setting delimiter"""
        # kwargs rewrite is necessery for being able to use dataset.export("csv")
        kwargs.pop("escape_output", None)
        if kwargs.pop("escape_html", None):
            self._escape_html(dataset)
        if kwargs.pop("escape_formulae", None):
            self._escape_formulae(dataset)

        kwargs["delimiter"] = ";"
        return dataset.export("csv", **kwargs)


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


def convert_to_date(date: str = None) -> datetime:
    """Convert string format %d/%m/%y %H:%M or %Y-%m-%d %H:%M:%S.%f to datetime"""

    formats_allowed = ["%d/%m/%y %H:%M", "%Y-%m-%d %H:%M:%S.%f", "%d-%m-%Y %H:%M","%Y-%m-%d %H:%M:%S"]

    _date = None

    for format in formats_allowed:
        try:
            _date = datetime.datetime.strptime(date, format)
            break
        except ValueError:
            pass

    if _date == None:
        raise ValueError(
            f"verkeerd datumformat voor {date}, toegestane formats zijn {formats_allowed}"
        )
    else:
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
