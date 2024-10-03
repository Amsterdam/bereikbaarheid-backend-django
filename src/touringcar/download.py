from abc import abstractmethod
from typing import Dict, List, Optional
from urllib.parse import urljoin

import requests
from django.conf import settings
from pyproj import Transformer

API_URL = urljoin(settings.BASE_URL, "v1/touringcar/")


class _Stop:
    transformer = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)

    latitude: float
    longitude: float
    text: str
    stop_type: str

    def __init__(self, entry: Dict) -> None:
        rdw_coordinates = entry["geometry"]["coordinates"]
        wgs_coordinates = self.transformer.transform(*rdw_coordinates)
        self.latitude = wgs_coordinates[1]
        self.longitude = wgs_coordinates[0]
        self._omschrijving = entry["omschrijving"]

    @property
    @abstractmethod
    def text(self) -> str: ...

    def to_row(self) -> List[str]:
        return [self.latitude, self.longitude, self.text, self.stop_type]


class Halte_data_api(_Stop):
    stop_type = "halte"

    @property
    def text(self) -> str:
        return self._omschrijving.split(":")[0]


class Parkeerplaats_data_api(_Stop):
    stop_type = "parkeerplaats"

    @property
    def text(self) -> str:
        return "".join(self._omschrijving.split(":")[1:]).strip()


def fetch_data() -> List[_Stop]:
    def _get_all(url: str, data_type: str, data: Optional[list] = None) -> Dict:
        data = [] if data is None else data

        response = requests.get(url).json()
        data = data + response["_embedded"][data_type]

        if "next" in response["_links"].keys():
            data = _get_all(response["_links"]["next"]["href"], data_type, data)
        return data

    haltes = [Halte_data_api(x) for x in _get_all(urljoin(API_URL, "haltes"), "haltes")]
    parkeerplaatsen = [
        Parkeerplaats_data_api(x)
        for x in _get_all(urljoin(API_URL, "parkeerplaatsen"), "parkeerplaatsen")
    ]
    return haltes + parkeerplaatsen
