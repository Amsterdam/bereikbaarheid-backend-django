from abc import abstractmethod
from typing import Dict, List

from pyproj import Transformer

from touringcar.models import Halte, Parkeerplaats


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


def fetch_data() -> List:
    # Fetch all haltes and parkeerplaatsen from the database
    haltes = [Halte_data_api(h) for h in Halte.objects.all()]
    parkeerplaatsen = [Parkeerplaats_data_api(p) for p in Parkeerplaats.objects.all()]

    return haltes + parkeerplaatsen
