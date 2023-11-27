from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from touringcar.model import Bericht

class BerichtSerializer(GeoFeatureModelSerializer):

    #geometry = GeometryField(source='bericht.geometry')
    serializers.ImageField(use_url=True, required=False, allow_null=True)

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
