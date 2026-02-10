from unittest.mock import MagicMock, patch

import pytest

from bereikbaarheid.bollards.bollards import _transform_results, get_bollards

QUERY_RESULT = [
    [
        (
            {
                "geometry": {
                    "type": "Point",
                    "crs": {"type": "name", "properties": {"name": "EPSG:4326"}},
                    "coordinates": [4.892034133000978, 52.37236150305945],
                },
                "properties": {
                    "id": "VC93",
                    "type": "ATM",
                    "location": "Kalverstraat inrit Dam",
                    "days": ["{ma", "di", "wo", "do", "vr", "za", "zo}"],
                    "start_time": "07:00:00",
                    "end_time": "23:59:00",
                    "entry_system": "Intercom",
                },
                "type": "Feature",
            },
        )
    ],
    [],
]


class TestBollards:
    @pytest.mark.parametrize("query_results", QUERY_RESULT)
    def test_transform_results(self, query_results):
        result = _transform_results(query_results)

        expected_results = [i[0] for i in query_results]
        assert result == expected_results

    def test_transform_results_none(self):
        assert _transform_results(None) == []

    @pytest.mark.django_db
    @patch(
        "bereikbaarheid.bollards.bollards.django_query_db",
        MagicMock(return_value=QUERY_RESULT[0]),
    )
    @pytest.mark.parametrize(
        "test_input",
        [
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
        ],
    )
    def test_get_bollards(self, test_input):
        """
        Mock the query result because of an empty db and check if the flow works
        with input parameters. Input parameters are not valid for the query result for
        this unit test because of the mock
        :return:
        """
        result = get_bollards(test_input)
        assert len(result) == 1
