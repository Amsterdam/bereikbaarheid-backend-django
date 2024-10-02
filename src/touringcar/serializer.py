from datetime import datetime

import pytz
from django.contrib.gis.geos import Point
from marshmallow import Schema, fields
from rest_framework import serializers
from rest_framework_gis.serializers import (
    GeoFeatureModelSerializer,
    GeometrySerializerMethodField,
)

from touringcar.models import (
    Bericht,
    Doorrijhoogte,
    Halte,
    Parkeerplaats,
    calc_lat_lon_from_geometry,
)

tz_amsterdam = pytz.timezone("Europe/Amsterdam")


class GeometryMixin(GeoFeatureModelSerializer):
    # a field which contains a geometry value and can be used as geo_field
    geom_wgs = GeometrySerializerMethodField()

    def get_geom_wgs(self, obj):
        wgs = calc_lat_lon_from_geometry(obj.geometry)
        # to be consistent with other-endpoints: serve lon,lat not lat,lon
        return Point(wgs["lon"], wgs["lat"])

    class Meta:
        abstract=True


class BerichtSerializer(GeometryMixin):

    image_url = serializers.ImageField(use_url=False)
    nl = serializers.SerializerMethodField()
    en = serializers.SerializerMethodField()
    fr = serializers.SerializerMethodField()
    de = serializers.SerializerMethodField()
    es = serializers.SerializerMethodField()

    @staticmethod
    def make_set(instance, lg):
        return {
            "title": getattr(instance, f"title{lg}"),
            "body": getattr(instance, f"body{lg}"),
            "advice": getattr(instance, f"advice{lg}"),
        }

    def get_nl(self, instance):
        return self.make_set(instance, "")

    def get_en(self, instance):
        return self.make_set(instance, "_en")

    def get_fr(self, instance):
        return self.make_set(instance, "_fr")

    def get_de(self, instance):
        return self.make_set(instance, "_de")

    def get_es(self, instance):
        return self.make_set(instance, "_es")

    class Meta:
        model = Bericht
        geo_field = "geom_wgs"

        fields = [
            "nl",
            "en",
            "fr",
            "de",
            "es",
            "id",
            "startdate",
            "enddate",
            "category",
            "link",
            "image_url",
            "important",
            "is_live",
        ]


class BerichtFilterSerializer(Schema):

    datum = fields.Date(
        format="%Y-%m-%d",
        load_default=datetime.today().astimezone(tz_amsterdam),
        required=False,
    )


class HalteSerializer(GeometryMixin):
    # change field names into dutch to connect frontend with same fields as old https://api.data.amsterdam.nl/v1/touringcars/
    omschrijving = serializers.CharField(source="name")
    bijzonderheden = serializers.CharField(source = "location")
    plaatsen = serializers.IntegerField( source = "capacity")
       
    class Meta:
        model = Halte
        geo_field = "geom_wgs"
        fields = [ "id",
                  "omschrijving",
                  "bijzonderheden",
                  "plaatsen",
                  "lat",
                  "lon",
                  "created_at",
                  "updated_at"]      
    

class ParkeerplaatsSerializer(GeometryMixin):
    omschrijving = serializers.CharField(source= "name")
    bijzonderheden = serializers.CharField(source = "location")
    plaatsen = serializers.IntegerField(source = "capacity")
    meerInformatie = serializers.CharField(source = "info")

    class Meta:
        model = Parkeerplaats
        geo_field = "geom_wgs"
        fields = [ "id",
                  "omschrijving",
                  "bijzonderheden",
                  "plaatsen",
                  "meerInformatie",
                  "url",
                  "lat",
                  "lon",
                  "created_at",
                  "updated_at"]
        

class DoorrijhoogteSerializer(GeometryMixin):
    omschrijving = serializers.CharField(source= "name")
    maximaleDoorrijhoogte = serializers.CharField(source= "maxheight")

    class Meta:
        model = Doorrijhoogte
        geo_field = "geom_wgs"
        fields = [ "id",
                  "omschrijving",
                  "maximaleDoorrijhoogte",
                  "lat",
                  "lon",
                  "created_at",
                  "updated_at"]