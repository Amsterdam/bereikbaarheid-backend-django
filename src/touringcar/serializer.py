from datetime import datetime

import pytz
from marshmallow import Schema, fields
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from touringcar.models import Bericht

tz_amsterdam = pytz.timezone("Europe/Amsterdam")


class BerichtSerializer(GeoFeatureModelSerializer):

    image_url = serializers.ImageField(use_url=True, required=False, allow_null=True)
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
        return self.make_set(instance,"")
    
    def get_en(self, instance):
        return self.make_set(instance,"_en")
    
    def get_fr(self, instance):
        return self.make_set(instance,"_fr")

    def get_de(self, instance):
        return self.make_set(instance,"_de")
    
    def get_es(self, instance):
        return self.make_set(instance,"_es")

    class Meta:
        model = Bericht
        geo_field = "geometry"

        fields = [
                "nl", "en", "fr", "de", "es",
                "startdate", "enddate", "category", 
                "link", "image_url", "important", "is_live",
         ]


class BerichtFilterSerializer(Schema):
    
    datum = fields.Date(
        format="%Y-%m-%d",
        load_default=datetime.today().astimezone(tz_amsterdam),
        required=False,
    )
