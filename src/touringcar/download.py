from abc import abstractmethod
from typing import List

from pyproj import Transformer

from touringcar.models import Halte, Parkeerplaats


class _Stop:
    transformer = Transformer.from_crs("EPSG:28992", "EPSG:4326", always_xy=True)

    def __init__(self, entry) -> None:
        wgs_coordinates = self.transformer.transform(entry.geometry.x, entry.geometry.y)
        self.latitude = wgs_coordinates[1]
        self.longitude = wgs_coordinates[0]
        self._omschrijving = entry.name

    @property
    @abstractmethod
    def text(self) -> str: ...

    @property
    def stop_type(self) -> str:
        raise NotImplementedError("Subclasses must define stop_type.")

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
    # Fetch all haltes and parkeerplaatsen from the database
    haltes = [Halte_data_api(h) for h in Halte.objects.all()]
    parkeerplaatsen = [Parkeerplaats_data_api(p) for p in Parkeerplaats.objects.all()]

    return haltes + parkeerplaatsen
