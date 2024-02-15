import csv
import json

from django.http import HttpResponse, JsonResponse
from marshmallow import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from bereikbaarheid.wrapper import extract_parameters
from touringcar.download import fetch_data
from touringcar.model import Bericht
from touringcar.serializer import BerichtFilterSerializer, BerichtSerializer


class BerichtList(APIView):

    def get(self, request):
        try:
            _params = extract_parameters(request)
            serialized_data = BerichtFilterSerializer().load(_params)
            
            #"Geeft een lijst terug met de berichten voor een dag"
            berichten = Bericht.objects.filter(startdate__lte = serialized_data['datum'], enddate__gte = serialized_data['datum'], is_live = True)
            serializer = BerichtSerializer(berichten, many=True, context={"request":request})

            return Response(serializer.data)   

        except ValidationError as err:
            return JsonResponse(status=400, data=err.messages)
        except json.JSONDecodeError as e:
            return JsonResponse(status=400, data={"error": str(e)})
    

class CsvView(APIView):
    def get(self, request):
        # TODO: Error handling
        try:
            response = HttpResponse(
                content_type="text/csv",
                headers={"Content-Disposition": 'attachment; filename="touringcar.csv"'},
            )

            writer = csv.writer(response)
            for entry in fetch_data():
                writer.writerow(entry.to_row())
        except err:
            response = JsonResponse(status=400, data={"error": str(err)})
        return response
