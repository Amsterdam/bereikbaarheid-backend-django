import pytest
from model_bakery import baker

from touringcar.model import DEFAULT_GEOM, Bericht


@pytest.fixture(scope="class")
def bericht_none():
    return baker.prepare(Bericht, geometry=None, lat=None, lon=None, pk=1 )

@pytest.fixture(scope="class")
def bericht_latlon():
    return baker.prepare(Bericht, geometry="SRID=28992;POINT (121278.2906402176 487150.7277812314)", lat=52.000000, lon=4.0000000, pk=2 )

@pytest.fixture(scope="class")
def bericht_geomnone():
    return baker.prepare(Bericht, geometry=None, lat=52.371198, lon=4.8920418, pk=3 )

@pytest.fixture(scope="class")
def bericht_geom():
    return baker.prepare(Bericht, geometry="SRID=28992;POINT (121278.2906402176 487150.7277812314)", lat=None, lon=None, pk=4 )


class TestModelSave:

    @pytest.mark.django_db    
    def test_save_ifnone(self, bericht_none):
        """geometry on DEFAULT so can changed by moving on the map"""
        bericht_none.save()
        assert Bericht.objects.get(pk=1).lat == None
        assert Bericht.objects.get(pk=1).lon == None
        assert str(Bericht.objects.get(pk=1).geometry) == DEFAULT_GEOM
        bericht_none.delete()
        assert not Bericht.objects.filter(pk=1).exists()

    @pytest.mark.django_db    
    def test_save_iflatlon(self, bericht_latlon):
        """consistency:  calculate lat,lon from given geometry 
        if geometry != DEFAULT_GEOM and lat,lon != None"""
        bericht_latlon.save()

        assert Bericht.objects.get(pk=2).lat == 52.371198006108706
        assert Bericht.objects.get(pk=2).lon == 4.892041799845697
        bericht_latlon.delete()
        assert not Bericht.objects.filter(pk=2).exists()    

    @pytest.mark.django_db    
    def test_save_ifgeomnone(self, bericht_geomnone):
        """geometry=None: calculate geometry from given lat,lon"""
        lat_org = bericht_geomnone.lat
        lon_org = bericht_geomnone.lon    

        bericht_geomnone.save()
        assert Bericht.objects.get(pk=3).lat == lat_org
        assert Bericht.objects.get(pk=3).lon == lon_org
        assert str(Bericht.objects.get(pk=3).geometry) == "SRID=28992;POINT (121278.2906402176 487150.7277812314)"
        bericht_geomnone.delete()
        assert not Bericht.objects.filter(pk=3).exists()   


    @pytest.mark.django_db    
    def test_save_ifgeom(self, bericht_geom):
        """geometry!=None lat,lon=None : keep as is"""
        geom_org = bericht_geom.geometry

        bericht_geom.save()
        assert Bericht.objects.get(pk=4).lat == None
        assert Bericht.objects.get(pk=4).geometry == geom_org
        bericht_geom.delete()
        assert not Bericht.objects.filter(pk=4).exists()  