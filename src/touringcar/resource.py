from django.contrib.gis.geos import GEOSGeometry
from import_export.resources import ModelResource

from touringcar.models import (
    Bericht,
    Doorrijhoogte,
    Halte,
    Parkeerplaats,
    calc_geometry_from_wgs,
)


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


class TouringcarBaseResource(ModelResource):
    def before_import(self, dataset, col_map, **kwargs):
        col_mapping = {
            "omschrijving": "name",
        }

        # combine col_mapping BaseResource and specificResource
        col_mapping |= col_map

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
        abstract = True


class HalteResource(TouringcarBaseResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "bijzonderheden": "location",
            "plaatsen": "capacity"
        }
        return super().before_import(dataset, col_mapping, **kwargs)

    class Meta:
        model = Halte
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("name",)


class ParkeerplaatsResource(TouringcarBaseResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "bijzonderheden": "location",
            "plaatsen": "capacity",
            "meerinformatie": "info",
        }
        return super().before_import(dataset, col_mapping, **kwargs)

    class Meta:
        model = Parkeerplaats
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("name",)


class DoorrijhoogteResource(TouringcarBaseResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "maximaledoorrijhoogte": "maxheight",
        }

        super().before_import(dataset, col_mapping, **kwargs)
        # add for use in import_id_fields
        dataset.headers.append('lat')
        dataset.headers.append('lon')

    class Meta:
        model = Doorrijhoogte
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("name", "lat", "lon")