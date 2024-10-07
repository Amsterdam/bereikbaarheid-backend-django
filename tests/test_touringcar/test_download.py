from unittest import mock

from django.test import TestCase

from touringcar.download import (
    Halte_data_api,
    Parkeerplaats_data_api,
    _Stop,
    fetch_data,
)
from touringcar.models import DEFAULT_GEOM, Halte, Parkeerplaats


class TestDownload(TestCase):
    def setUp(self):
        self.halte = Halte.objects.create(
            name="H7: Spui",
            location="Nieuwezijds Voorburgwal 355",
            capacity=1,
            geometry=DEFAULT_GEOM,
        )
        self.parkeerplaats = Parkeerplaats.objects.create(
            name="P1: P+R Zeeburg",
            location="Zuiderzeeweg 46A.",
            capacity=20,
            info="http://www.amsterdam.nl/parkeren",
            url="http://www.amsterdam.nl/parkeren",
            geometry=DEFAULT_GEOM,
        )

    @mock.patch("touringcar.models.Halte.objects.all")
    @mock.patch("touringcar.models.Parkeerplaats.objects.all")
    def test_fetch_data_returns_haltes_parkeerplaatsen(
        self, mock_parkeerplaats, mock_halte
    ):
        mock_halte.return_value = [self.halte]
        mock_parkeerplaats.return_value = [self.parkeerplaats]

        haltes_parkeerplaatsen = fetch_data()

        for x in haltes_parkeerplaatsen:
            self.assertIsInstance(x, (Halte_data_api, Parkeerplaats_data_api))

    def test_stop_converts_location_data_rdw_to_wgs(self):
        stop = _Stop(self.halte)

        # Verify latitude and longitude are as expected (converted from RDW to WGS)
        self.assertAlmostEqual(stop.latitude, 52.380983037141235, places=6)
        self.assertAlmostEqual(stop.longitude, 4.902911287841951, places=6)

    def test_halte_formats_text(self):
        halte_data_api = Halte_data_api(self.halte)

        self.assertEqual(halte_data_api.text, "H7")

    def test_parkeerplaats_formats_text(self):
        parkeerplaats_data_api = Parkeerplaats_data_api(self.parkeerplaats)

        self.assertEqual(parkeerplaats_data_api.text, "P+R Zeeburg")
