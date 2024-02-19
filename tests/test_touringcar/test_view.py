import json
from datetime import datetime
from unittest import mock

import geojson
import pytest
import pytz
from django.core.exceptions import ValidationError
from model_bakery import baker

from touringcar.download import Halte, Parkeerplaats
from touringcar.model import Bericht
from touringcar.serializer import BerichtFilterSerializer, BerichtSerializer

tz_amsterdam = pytz.timezone("Europe/Amsterdam")


@pytest.fixture
def bericht_today():
    return baker.prepare(Bericht, is_live=True, startdate=datetime.today().astimezone(tz_amsterdam), enddate = datetime.today().astimezone(tz_amsterdam))

@pytest.fixture
def bericht_error():
    return baker.prepare(Bericht, is_live=True, startdate="2023-11-15", enddate = "2023-11-04")


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
            ("?datum=2023-11-28", 200), ("?datum=",200),
            ("?datum=2023", 400), ("?datum=2023/11/28", 400), ("?datum=28-11-2023", 400),
        ],
    )
def test_get_status_code(client, test_input, expected):
    url_param = "/v1/touringcar/berichten" + f"{test_input}"
    response = client.get(url_param)
    assert response.status_code == expected

@pytest.mark.django_db
def test_get_bericht_noparam(client, bericht_today):
    bericht_today.save()
    response = client.get("/v1/touringcar/berichten")
    result = geojson.loads(response.content.decode("utf-8"))
    assert result["features"][0]["properties"]["startdate"] == bericht_today.startdate.strftime("%Y-%m-%d")

def test_serves_csv(client):
    with mock.patch("touringcar.view.fetch_data") as fetch_data:
        fetch_data.return_value = [
            Halte({
                "omschrijving": "H7: Spui",
                "geometry": {
                    "coordinates": [
                        121180.61543053293,
                        487116.3467369651
                    ]
                }
            }),
            Parkeerplaats({
                "omschrijving": "P1: P+R Zeeburg",
                "geometry": {
                    "coordinates": [
                        126035.35254910096,
                        487121.07517851336
                    ]
                }
            }),
        ]
        response = client.get("/v1/touringcar/downloads")
    
    assert response.status_code == 200
    assert response.headers["Content-Disposition"] == "attachment; filename=\"touringcar.csv\""
    assert response.headers["Content-Type"] == "text/csv"
    assert response.content == b'4.8906110012279225,52.37088300414084,H7,halte\r\n4.961894001299134,52.37120300414078,P+R Zeeburg,parkeerplaats\r\n'
