import pytest
from django.contrib.gis.geos import GEOSGeometry
from django.core.exceptions import ValidationError
from model_bakery import baker

from touringcar.models import DEFAULT_GEOM, Doorrijhoogte

GEO_NONE =  Doorrijhoogte(
        name = "geo_none", 
        lat = None,
        lon = None,
        geometry = None,
        maxheight = "4m"
        )

CALC_LAT_LON = Doorrijhoogte(
        name ="calc_lat_lon", 
        lat = 52.000000,
        lon = 4.0000000,
        geometry= "SRID=28992;POINT (121278.2906402176 487150.7277812314)",
        maxheight = "4,1m"
        ) 

GEODEFAULT = Doorrijhoogte(
        name ="geomdefault", 
        lat = 52.371198,
        lon = 4.892042,
        geometry= DEFAULT_GEOM,
        maxheight = "4,25m"
        )       

GEOM = Doorrijhoogte(
        name ="geom", 
        lat = None,
        lon = None,
        geometry= "SRID=28992;POINT (121278.2906402176 487150.7277812314)",
        maxheight = "40,1m"
        )    


class TestModelSave:
    @pytest.mark.django_db
    def test_save_geom_none(self):
        """geometry always on DEFAULT not allowed to be None"""
        with pytest.raises(ValidationError) as e:
            GEO_NONE.save()

        assert "{'geometry': ['This field cannot be null.']" in str(e.value)

    @pytest.mark.django_db
    def test_save_iflatlon(self):
        """consistency:  calculate lat,lon from given geometry
        if geometry != DEFAULT_GEOM and lat,lon != None"""
        CALC_LAT_LON.save()

        assert Doorrijhoogte.objects.last().lat == 52.371198
        assert Doorrijhoogte.objects.last().lon == 4.892042
        CALC_LAT_LON.delete()
        assert Doorrijhoogte.objects.count() == 0

    @pytest.mark.django_db
    def test_save_ifgeomdefault(self):
        """calculate geometry from given lat,lon"""
        lat_org = GEODEFAULT.lat
        lon_org = GEODEFAULT.lon

        GEODEFAULT.save()
        assert Doorrijhoogte.objects.last().lat == lat_org
        assert Doorrijhoogte.objects.last().lon == lon_org
        assert Doorrijhoogte.objects.last().geometry.equals_exact(
                GEOSGeometry("SRID=28992;POINT (121278.3042605289 487150.7276881739)"), tolerance=0.005
            )  # because of decimals == comparing not true

        GEODEFAULT.delete()
        assert Doorrijhoogte.objects.count() == 0

    @pytest.mark.django_db
    def test_save_ifgeom(self):
        """geometry!=None lat,lon=None : keep as is"""
        geom_org = GEOM.geometry

        GEOM.save()
        assert Doorrijhoogte.objects.last().lat == None
        assert Doorrijhoogte.objects.last().geometry == geom_org
        GEOM.delete()
        assert Doorrijhoogte.objects.count() == 0

    @pytest.mark.parametrize(
        "testheight",
        [
            ("$"),
            ("4,,"),
            ("4"),
            ("4m2"),
            ("4.1m"),
        ],
    )
    @pytest.mark.django_db
    def test_save_maxdoorrijhoogte(self, testheight):
        with pytest.raises(ValidationError) as excinfo:
            test = baker.prepare(Doorrijhoogte, maxheight = testheight)
            test.full_clean()

        assert "format voor maximaledoorijhoogte" in str(excinfo.value)