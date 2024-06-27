import geojson
import pytest
from django.db import connection
from model_bakery import baker

from bereikbaarheid.models import VerkeersPaal


@pytest.fixture(autouse=True)
def activate_postgis_pgrouting():
    with connection.cursor() as cursor:
        cursor.execute("CREATE EXTENSION IF NOT EXISTS pgrouting;")


@pytest.fixture
def bollard():
    """Fixture for baked Verkeerspaal model"""
    return baker.make(VerkeersPaal, bijzonderheden="Bij calamiteiten bellen")


class TestViews:
    def setup_method(self):
        self.url = "/api/v1/"

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("bollards/", 200),
            ("road-elements/1/", 200),
            ("road-sections/load-unload/", 200),
            ("traffic-signs/", 400),  # needs params
            ("permits/", 400),  # needs params
            ("roads/prohibitory/", 400),  # needs params
            ("roads/isochrones/", 400),  # needs params
        ],
    )
    @pytest.mark.django_db
    def test_get_status_code(self, client, test_input, expected):
        response = client.get(self.url + test_input)
        assert response.status_code == expected

    @pytest.mark.django_db
    def test_get_bollards_noparam(self, client, bollard):
        bollard.save()
        response = client.get(self.url + "bollards/")
        result = geojson.loads(response.content.decode("utf-8"))
        assert result["features"][0]["properties"]["details"] == bollard.bijzonderheden

    @pytest.mark.parametrize(
        "test_input, test_params, expected",
        [
            (
                "bollards/",
                "?dayOfTheWeek=di&lat=52.371198&lon=4.8920418&timeFrom=13:00&timeTo=12:00",
                400,
            ),
            (
                "traffic-signs/",
                "?trafficSignCategories=prohibition&&vehicleAxleWeight=10000&vehicleHasTrailer=false&vehicleHeight=2.65&vehicleLength=8.23&vehicleMaxAllowedWeight=26500&vehicleTotalWeight=26500&vehicleType=Bedrijfsauto&vehicleWidth=2.55",
                200,
            ),
            (
                "bollards/",
                "?dayOfTheWeek=di&lat=52.371198&lon=4.8920418&timeFrom=06:00&timeTo=12:00",
                200,
            ),
            (
                "permits/",
                "?lat=52.37329259746784&lon=4.89371756804882&permitLowEmissionZone=false&permitZzv=true&vehicleAxleWeight=10000&vehicleHasTrailer=false&vehicleHeight=2.65&vehicleLength=8.23&vehicleTotalWeight=26500&vehicleType=Bedrijfsauto&vehicleWidth=2.55&vehicleMaxAllowedWeight=26500",
                200,
            ),  # needs params
            (
                "roads/prohibitory/",
                "?permitLowEmissionZone=false&permitZzv=true&vehicleAxleWeight=10000&vehicleHasTrailer=false&vehicleHeight=2.65&vehicleLength=8.23&vehicleTotalWeight=26500&vehicleType=Bedrijfsauto&vehicleWidth=2.55&vehicleMaxAllowedWeight=26500",
                200,
            ),
            ("roads/isochrones/", "?lat=52.371198&lon=4.8920418", 200),
        ],
    )
    @pytest.mark.django_db
    def test_with_params(self, client, test_input, test_params, expected):
        url = self.url + test_input + test_params
        response = client.get(url)
        assert response.status_code == expected
