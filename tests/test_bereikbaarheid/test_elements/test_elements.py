from unittest.mock import MagicMock, patch

import pytest

from bereikbaarheid.elements.elements import _transform_results, get_elements, raw_query
from bereikbaarheid.utils import django_query_db

QUERY_RESULT = [
    (
        {
            "type": "MultiLineString",
            "coordinates": [[[4.910313956896239, 52.40562576579803]]],
        },
        28234,
        29,
        30,
        "Botterstraat",
        [
            {
                "direction_1": "Noord (richting Sloterweg)",
                "direction_2": "Zuid (richting A4)",
                "known_interruptions": "Geen;",
                "langzaam_verkeer": True,
                "link_to_file": "https://verkeeramsterdam.nl/verkeerstellingen/Anderlechtlaan.Tel2016.xls",
                "location_name": "Telpunt: Anderlechtlaan",
                "measures_between": "A4 - Sloterweg",
                "method": "Telslang",
                "remarks": "Geen;",
                "snelverkeer": True,
                "traffic_type": "beide",
                "year": 2016,
            }
        ],
        [],
    )
]


class TestElements:
    @pytest.mark.django_db
    def test_raw_query(self):
        """
        Only test the query to see if the structure and parameters are working.
        No data is returning because of empty database
        :return:
        """

        result = django_query_db(raw_query, {"road_element_id": 1})
        assert result == []

    @pytest.mark.parametrize(
        "query_results, expected_result",
        [
            (
                QUERY_RESULT,
                [
                    {
                        "type": "Feature",
                        "geometry": QUERY_RESULT[0][0],
                        "properties": {
                            "id": QUERY_RESULT[0][1],
                            "length_in_m": QUERY_RESULT[0][2],
                            "max_speed_in_km": QUERY_RESULT[0][3],
                            "street_name": QUERY_RESULT[0][4],
                            "traffic_counts": QUERY_RESULT[0][5],
                        },
                    }
                ],
            )
        ],
    )
    def test__transform_results(self, query_results, expected_result):
        result = _transform_results(query_results)
        assert result == expected_result

    @patch(
        "bereikbaarheid.elements.elements.django_query_db",
        MagicMock(return_value=QUERY_RESULT),
    )
    def test_get_elements(self):
        """
        Mock the query result because of an empty db and check if the flow works
        with input parameters. Input parameters are not valid for the query result for
        this unit test because of the mock
        :return:
        """
        result = get_elements(element_id=1)
        assert len(result) == 1
