from django.urls import path

from touringcar.view import (
    BerichtList,
    CsvView,
    DoorrijhoogteList,
    HalteList,
    ParkeerplaatsList,
)

urlpatterns = [
    path("v1/touringcar/berichten", BerichtList.as_view()),
    path("v1/touringcar/haltes", HalteList.as_view()),
    path("v1/touringcar/parkeerplaatsen", ParkeerplaatsList.as_view()),
    path("v1/touringcar/doorrijhoogten", DoorrijhoogteList.as_view()),
    path("v1/touringcar/downloads/csv", CsvView.as_view()),
]
