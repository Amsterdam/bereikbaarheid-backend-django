import pytest
from marshmallow import ValidationError

from bereikbaarheid.bollards.serializer import BollardsSerializer


class TestBollardsSerializer:
    # (1 item) /v1/bollards/?dayOfTheWeek=di&lat=52.371198&lon=4.8920418&timeFrom=06:00&timeTo=12:00
    # (2 items) /v1/bollards/?dayOfTheWeek=di&lat=52.356221&lon=4.896677&timeFrom=10:00&timeTo=12:00
    # (geen resultaat) /v1/bollards/?dayOfTheWeek=di&lat=52.361595&lon=4.870919&timeFrom=10:00&timeTo=12:00

    params_valid = [
        {
            "dayOfTheWeek": "di",
            "lat": "52.371198",
            "lon": "4.8920418",
            "timeFrom": "06:00",
            "timeTo": "12:00",
        },
        {
            "lat": "52.371198",
            "lon": "4.8920418",
        },
    ]

    params_invalid = [
        {
            "dayOfTheWeek": "di",
            "lat": "52.371198",
            "lon": "4.8920418",
            "timeFrom": "23:00",
            "timeTo": "15:00",
        },
        {
            "dayOfTheWeek": "di",
            "lat": "52.371198",
            "lon": "4.8920418",
            "timeFrom": "06:00",
        },
        {
            "dayOfTheWeek": "di",
            "lat": "52.371198",
            "lon": "4.8920418",
            "timeTo": "06:00",
        },
        {
            "lat": "52.371198",
            "lon": "4.8920418",
            "timeFrom": "23:00",
            "timeTo": "15:00",
        },
    ]

    @pytest.mark.parametrize("test_input", params_valid)
    def test_serializer_validate(self, test_input):
        BollardsSerializer().load(test_input)

    @pytest.mark.parametrize("test_input", params_invalid)
    def test_serilizer_validate_ERROR(self, test_input):
        with pytest.raises(ValidationError):
            BollardsSerializer().load(test_input)
