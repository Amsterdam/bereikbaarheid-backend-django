from unittest import mock
from urllib.parse import urljoin

from touringcar.download import API_URL, Halte, Parkeerplaats, _Stop, fetch_data


class TestDownload:
    api_responses = [
        {
            "_embedded": {
                "haltes": [
                    {
                        "_links": {
                            "schema": "https://schemas.data.amsterdam.nl/datasets/touringcars/dataset#haltes",
                            "self": {
                                "href": "https://api.data.amsterdam.nl/v1/touringcars/haltes/1/",
                                "title": "H7: Spui",
                                "id": 1,
                            },
                        },
                        "id": 1,
                        "geometry": {
                            "type": "Point",
                            "coordinates": [121180.61543053293, 487116.3467369651],
                        },
                        "omschrijving": "H7: Spui",
                        "bijzonderheden": "Nieuwezijds Voorburgwal 355",
                        "plaatsen": "1",
                    },
                ]
            },
            "_links": {"next": {"href": "next!"}},
        },
        {"_embedded": {"haltes": []}, "_links": {}},
        {
            "_embedded": {
                "parkeerplaatsen": [
                    {
                        "_links": {
                            "schema": "https://schemas.data.amsterdam.nl/datasets/touringcars/dataset#parkeerplaatsen",
                            "self": {
                                "href": "https://api.data.amsterdam.nl/v1/touringcars/parkeerplaatsen/1/",
                                "title": "P1: P+R Zeeburg",
                                "id": 1,
                            },
                        },
                        "id": 1,
                        "geometry": {
                            "type": "Point",
                            "coordinates": [126035.35254910096, 487121.07517851336],
                        },
                        "omschrijving": "P1: P+R Zeeburg",
                        "bijzonderheden": "Zuiderzeeweg 46A. Tarief: 1-3H: € 7,50 | >1H: €2,50 | 24H: € 22,50.",
                        "plaatsen": "20",
                        "meerInformatie": "http://www.amsterdam.nl/parkeren",
                        "url": "http://www.amsterdam.nl/parkeren",
                    },
                ]
            },
            "_links": {"next": {"href": "next!"}},
        },
        {"_embedded": {"parkeerplaatsen": []}, "_links": {}},
    ]

    def test_fetch_data_fetches_next_page_when_present(self):
        with mock.patch("touringcar.download.requests.get") as get:
            get.return_value.json.side_effect = self.api_responses

            fetch_data()

            get.assert_has_calls(
                [
                    mock.call(urljoin(API_URL, "haltes")),
                    mock.call().json(),
                    mock.call("next!"),
                    mock.call().json(),
                    mock.call(urljoin(API_URL, "parkeerplaatsen")),
                    mock.call().json(),
                    mock.call("next!"),
                    mock.call().json(),
                ]
            )

    def test_fetch_data_returns_haltes_parkeerplaatsen(self):
        with mock.patch("touringcar.download.requests.get") as get:
            get.return_value.json.side_effect = self.api_responses

            haltes_parkeerplaatsen = fetch_data()

        for x in haltes_parkeerplaatsen:
            assert type(x) in [Halte, Parkeerplaats]

    def test_stop_converts_location_data_rdw_to_wgs(self):
        stop = _Stop(self.api_responses[0]["_embedded"]["haltes"][0])

        assert stop.latitude == 52.37088300414084
        assert stop.longitude == 4.8906110012279225

    def test_halte_formats_text(self):
        halte = Halte(self.api_responses[0]["_embedded"]["haltes"][0])

        assert halte.text == "H7"

    def test_parkeerplaats_formats_text(self):
        halte = Parkeerplaats(self.api_responses[2]["_embedded"]["parkeerplaatsen"][0])

        assert halte.text == "P+R Zeeburg"
