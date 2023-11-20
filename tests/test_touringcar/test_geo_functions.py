import pytest
from django.contrib.gis.geos import Point

from touringcar.model import calc_geometry_from_wgs, calc_lat_lon_from_geometry


class TestGeoFunctions:

    @pytest.mark.parametrize( "test_lat, test_lon, expected",[ (52.37824890, 4.90733317, "SRID=28992;POINT (122324.8518969522 487928.2283529527)")])
    def test_calc_geometry_from_wgs(self, test_lat, test_lon, expected):
        '''Calculate geometry in srid=28992 (RD-coordinates) from given latitude and longitude (srid=4326; WGS coordinates)'''
        assert str(calc_geometry_from_wgs(test_lat, test_lon)) == expected
        
    @pytest.mark.parametrize( "test_x, test_y, expected",[ (122324.8518969522, 487928.2283529527, {'lat':52.378248906112546, 'lon':4.907333169860667})])        
    def test_calc_lat_lon_from_geometry(self, test_x, test_y, expected):
        '''Calculate Point latitude and longitude (srid=4326; WGS coordinates) from given geometry in srid=28992 (RD-coordinates)''' 
        assert calc_lat_lon_from_geometry(Point( test_x, test_y, srid=28992)) == expected
