import csv
import json
import logging

from django.http import HttpResponse, JsonResponse
from marshmallow import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from bereikbaarheid.wrapper import extract_parameters
from touringcar.download import fetch_data
from touringcar.models import Bericht, Doorrijhoogte, Halte, Parkeerplaats
from touringcar.serializer import (
    BerichtFilterSerializer,
    BerichtSerializer,
    DoorrijhoogteSerializer,
    HalteSerializer,
    ParkeerplaatsSerializer,
)

log = logging.getLogger(__name__)


class BerichtList(APIView):
    def get(self, request):
        try:
            _params = extract_parameters(request)
            serialized_data = BerichtFilterSerializer().load(_params)

            # "Geeft een lijst terug met de berichten voor een dag"
            berichten = Bericht.objects.filter(
                startdate__lte=serialized_data["datum"],
                enddate__gte=serialized_data["datum"],
                is_live=True,
            )
            serializer = BerichtSerializer(
                berichten, many=True, context={"request": request}
            )

            return Response(serializer.data)

        except ValidationError as err:
            log.info(err.messages)
            return JsonResponse(status=400, data={"error": "An error has occurred!"})
        except json.JSONDecodeError as e:
            log.info(str(e))
            return JsonResponse(status=400, data={"error": "An error has occurred!"})


class CsvView(APIView):
    def get(self, request):
        try:
            response = HttpResponse(
                content_type="text/csv",
                headers={
                    "Content-Disposition": 'attachment; filename="touringcar.csv"'
                },
            )

            writer = csv.writer(response)
            for entry in fetch_data():
                writer.writerow(entry.to_row())
        except Exception as err:
            log.info(str(err))
            response = JsonResponse(
                status=400, data={"error": "An error has occurred!"}
            )
        return response


class HalteList(APIView):
    def get(self, request):
        print("trying1")
        try:
            print("trying2")
            # "Geeft een lijst terug met alle haltes"
            serializer = HalteSerializer(Halte.objects.all(), many=True)
            print("trying3")
            return Response(serializer.data)

        except Exception as err:
            log.info(str(err))
            return JsonResponse(status=400, data={"error": "An error has occurred!"})


class ParkeerplaatsList(APIView):
    def get(self, request):
        try:
            # "Geeft een lijst terug met alle haltes"
            serializer = ParkeerplaatsSerializer(Parkeerplaats.objects.all(), many=True)
            return Response(serializer.data)

        except Exception as err:
            log.info(str(err))
            return JsonResponse(status=400, data={"error": "An error has occurred!"})


class DoorrijhoogteList(APIView):
    def get(self, request):
        try:
            # "Geeft een lijst terug met alle haltes"
            serializer = DoorrijhoogteSerializer(Doorrijhoogte.objects.all(), many=True)
            return Response(serializer.data)

        except Exception as err:
            log.info(str(err))
            return JsonResponse(status=400, data={"error": "An error has occurred!"})
