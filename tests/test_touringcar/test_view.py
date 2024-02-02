import json
from datetime import datetime

import geojson
import pytest
import pytz
from django.core.exceptions import ValidationError
from model_bakery import baker

from touringcar.models import Bericht
from touringcar.serializer import BerichtFilterSerializer, BerichtSerializer

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
