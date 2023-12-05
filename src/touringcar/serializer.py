from datetime import datetime

import pytz
from marshmallow import Schema, fields
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from touringcar.model import Bericht

tz_amsterdam = pytz.timezone("Europe/Amsterdam")


class BerichtSerializer(GeoFeatureModelSerializer):

    image_url = serializers.ImageField(use_url=True, required=False, allow_null=True)

    class Meta:
        model = Bericht
        geo_field = "geometry"

        fields = [
            "title", "body", "advice",
            "title_en", "body_en", "advice_en",
            "title_fr", "body_fr", "advice_fr",
            "title_de", "body_de", "advice_de",
            "title_es", "body_es", "advice_es",
            "startdate", "enddate", "category", 
            "link", "image_url", "important", "is_live"
         ]


class BerichtFilterSerializer(Schema):
    
    datum = fields.Date(
        format="%Y-%m-%d",
        load_default= datetime.today().astimezone(tz_amsterdam),
        required=False,
    )
