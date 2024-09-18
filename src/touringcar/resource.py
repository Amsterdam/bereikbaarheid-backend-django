from django.contrib.gis.geos import GEOSGeometry
from import_export.resources import ModelResource

from touringcar.models import Bericht, Halte, Parkeerplaats, calc_geometry_from_wgs


class BerichtResource(ModelResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "location_lat": "lat",
            "location_lng": "lon",
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]

        # trim leading and trailing spaces
        title_clean = [x.strip() for x in dataset["title"]]
        del dataset["title"]
        dataset.append_col(title_clean, header="title")

    class Meta:
        model = Bericht
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("title", "startdate", "enddate")


class HalteResource(ModelResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "omschrijving": "name",
            "bijzonderheden": "location",
            "plaatsen": "capacity"
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]
        
        # trim leading and trailing spaces
        name_clean = [x.strip() for x in dataset["name"]]
        del dataset["name"]
        dataset.append_col(name_clean, header="name")

        # Rename the column
        dataset.headers[dataset.headers.index("geom")] = "geometry"


    def before_import_row(self, row, **kwargs):
        geom = GEOSGeometry(str(row["geometry"]))
        row["lat"] = geom.y
        row["lon"] = geom.x
        
        if geom.srid == 4326:
            row["geometry"] = calc_geometry_from_wgs(geom.y, geom.x)
        else:
            row["geometry"] = geom

    class Meta:
        model = Halte
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("name",)


class ParkeerplaatsResource(ModelResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "omschrijving": "name",
            "bijzonderheden": "location",
            "plaatsen": "capacity",
            "meerinformatie": "info",
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]
        
        # trim leading and trailing spaces
        name_clean = [x.strip() for x in dataset["name"]]
        del dataset["name"]
        dataset.append_col(name_clean, header="name")

        # Rename the column
        dataset.headers[dataset.headers.index("geom")] = "geometry"


    def before_import_row(self, row, **kwargs):
        geom = GEOSGeometry(str(row["geometry"]))
        row["lat"] = geom.y
        row["lon"] = geom.x
        
        if geom.srid == 4326:
            row["geometry"] = calc_geometry_from_wgs(geom.y, geom.x)
        else:
            row["geometry"] = geom

    class Meta:
        model = Parkeerplaats
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("name",)        