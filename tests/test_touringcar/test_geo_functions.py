import pytest
from django.contrib.gis.geos import GEOSGeometry, Point

from touringcar.models import calc_geometry_from_wgs, calc_lat_lon_from_geometry


class TestGeoFunctions:
    @pytest.mark.parametrize(
        "test_lat, test_lon, expected",
        [
            (
                52.378248,
                4.907333,
                "SRID=28992;POINT (122324.8396584391 487928.1282926429)",
            )
        ],
    )
    def test_calc_geometry_from_wgs(self, test_lat, test_lon, expected):
        """Calculate geometry in srid=28992 (RD-coordinates) from given latitude and longitude (srid=4326; WGS coordinates)"""
        test_calcgeom = calc_geometry_from_wgs(test_lat, test_lon)
        assert test_calcgeom.equals_exact(
            GEOSGeometry(expected), tolerance=0.005
        )  # because of decimals == comparing not true

    @pytest.mark.parametrize(
        "test_x, test_y, expected",
        [
            (
                122324.85654776845,
                487928.22845181637,
                {"lat": 52.378249, "lon": 4.907333},
            )
        ],
    )
    def test_calc_lat_lon_from_geometry(self, test_x, test_y, expected):
        """Calculate Point latitude and longitude (srid=4326; WGS coordinates) from given geometry in srid=28992 (RD-coordinates)"""
        dict = calc_lat_lon_from_geometry(Point(test_x, test_y, srid=28992))
        assert round(dict["lat"], 6) == expected["lat"]
        assert round(dict["lon"], 6) == expected["lon"]
