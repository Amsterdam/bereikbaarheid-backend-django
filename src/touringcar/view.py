from rest_framework.response import Response
from rest_framework.views import APIView

from touringcar.serializer import BerichtSerializer
from touringcar.model import Bericht

from datetime import datetime

class BerichtList(APIView):

    def get(self, request):
        live_berichten = Bericht.objects.filter(enddate__gt = datetime.today().date(),is_live = True)
        serializer = BerichtSerializer(live_berichten, many=True)
        return Response(serializer.data)