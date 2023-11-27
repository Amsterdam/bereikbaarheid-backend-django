from django.urls import path

from touringcar.view import BerichtList
urlpatterns = [
    path("v1/touringcar/berichten", BerichtList.as_view()),
]