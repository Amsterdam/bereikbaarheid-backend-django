from django.urls import path

from touringcar.view import BerichtList, CsvView

urlpatterns = [
    path("v1/touringcar/berichten", BerichtList.as_view()),
    path("v1/touringcar/downloads/csv", CsvView.as_view()),
]