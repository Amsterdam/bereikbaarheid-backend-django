import json
from datetime import datetime
from unittest import mock

import geojson
import pytest
import pytz
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from model_bakery import baker

from touringcar.download import Halte_data_api, Parkeerplaats_data_api
from touringcar.models import DEFAULT_GEOM, Bericht, Doorrijhoogte, Halte, Parkeerplaats
from touringcar.serializer import (
    BerichtSerializer,
    DoorrijhoogteSerializer,
    HalteSerializer,
    ParkeerplaatsSerializer,
)

tz_amsterdam = pytz.timezone("Europe/Amsterdam")
api_path = "/api/v1/"


@pytest.fixture
def bericht_today():
    return baker.prepare(
        Bericht,
        is_live=True,
        startdate=datetime.today().astimezone(tz_amsterdam),
        enddate=datetime.today().astimezone(tz_amsterdam),
    )


@pytest.fixture
def bericht_error():
    return baker.prepare(
        Bericht, is_live=True, startdate="2023-11-15", enddate="2023-11-04"
    )


@pytest.mark.django_db
def test_error_start_enddate(bericht_error):
    with pytest.raises(ValidationError) as e:
        bericht_error.save()
    assert "{'enddate': ['enddate can not be before startdate.']}" == e.value.__str__()


@pytest.mark.django_db
def test_serialization(bericht_today):
    bericht_today.save()
    serializer = BerichtSerializer(bericht_today)
    data = serializer.data
    assert data["properties"]["is_live"] == True


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_input, expected",
    [
        ("", 200),
        ("?datum=2023-11-28", 200),
        ("?datum=", 200),
        ("?datum=2023", 400),
        ("?datum=2023/11/28", 400),
        ("?datum=28-11-2023", 400),
    ],
)
def test_get_status_code(client, test_input, expected):
    url_param = api_path + "touringcar/berichten" + f"{test_input}"
    response = client.get(url_param)
    assert response.status_code == expected


@pytest.mark.django_db
def test_get_bericht_noparam(client, bericht_today):
    bericht_today.save()
    response = client.get(api_path + "touringcar/berichten")
    result = geojson.loads(response.content.decode("utf-8"))
    assert result["features"][0]["properties"][
        "startdate"
    ] == bericht_today.startdate.strftime("%Y-%m-%d")


@pytest.mark.django_db
def test_serves_csv(client):
    # Create mock instances of Halte and Parkeerplaats
    halte = Halte.objects.create(
        name="H7: Spui",
        geometry=Point(121180.61543053293, 487116.3467369651),
        location="Nieuwezijds Voorburgwal 355",
        capacity=1,
    )
    parkeerplaats = Parkeerplaats.objects.create(
        name="P1: P+R Zeeburg",
        geometry=Point(126035.35254910096, 487121.07517851336),
        location="Zuiderzeeweg 46A.",
        capacity=20,
    )

    response = client.get("/api/v1/touringcar/downloads/csv")

    assert response.status_code == 200
    assert (
        response.headers["Content-Disposition"]
        == 'attachment; filename="touringcar.csv"'
    )
    assert response.headers["Content-Type"] == "text/csv"
    assert (
        response.content
        == b"52.37088300414084,4.8906110012279225,H7,halte\r\n52.37120300414078,4.961894001299134,P+R Zeeburg,parkeerplaats\r\n"
    )


HALTE_TEST = Halte(
    name="H1: test",
    lat=52.37088300,
    lon=4.890611,
    geometry=DEFAULT_GEOM,
    location="test test",
    capacity=5,
)


PARKEERPLAATS_TEST = Parkeerplaats(
    name="P1: test",
    lat=52.97088300,
    lon=4.890611,
    geometry=DEFAULT_GEOM,
    location="test test",
    capacity=5,
    info="testtest",
)

DOORRIJHOOGTE_TEST = Doorrijhoogte(
    name="Doorrijhoogte test",
    lat=52.47088300,
    lon=4.890611,
    geometry=DEFAULT_GEOM,
    maxheight="4m",
)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_model, test_input, test_serializer, expected",
    [
        (Halte, HALTE_TEST, HalteSerializer, "H1: test"),
        (Parkeerplaats, PARKEERPLAATS_TEST, ParkeerplaatsSerializer, "P1: test"),
        (
            Doorrijhoogte,
            DOORRIJHOOGTE_TEST,
            DoorrijhoogteSerializer,
            "Doorrijhoogte test",
        ),
    ],
)
def test_serialization_halte(test_model, test_input, test_serializer, expected):
    test_input.save()
    serializer = test_serializer(test_input)
    data = serializer.data
    assert data["properties"]["omschrijving"] == expected

    test_input.delete()
    assert test_model.objects.count() == 0


@pytest.mark.django_db
@pytest.mark.parametrize(
    "test_model, test_path, test_input, test_var, expected",
    [
        (Halte, "/haltes", HALTE_TEST, "lat", HALTE_TEST.lat),
        (
            Parkeerplaats,
            "/parkeerplaatsen",
            PARKEERPLAATS_TEST,
            "meerInformatie",
            PARKEERPLAATS_TEST.info,
        ),
        (
            Doorrijhoogte,
            "/doorrijhoogten",
            DOORRIJHOOGTE_TEST,
            "maximaleDoorrijhoogte",
            DOORRIJHOOGTE_TEST.maxheight,
        ),
    ],
)
def test_get_halte(client, test_model, test_path, test_input, test_var, expected):
    test_input.save()
    response = client.get(api_path + "touringcar" + test_path)
    result = geojson.loads(response.content.decode("utf-8"))

    assert result["features"][0]["properties"][test_var] == expected
    assert result["features"][0]["geometry"]["coordinates"] != DEFAULT_GEOM

    test_input.delete()
    assert test_model.objects.count() == 0
