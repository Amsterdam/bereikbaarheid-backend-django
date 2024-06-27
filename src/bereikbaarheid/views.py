import json

from django.http import HttpRequest, JsonResponse
from django.views import View
from marshmallow import ValidationError

from bereikbaarheid.bollards import get_bollards
from bereikbaarheid.bollards.serializer import BollardsSerializer
from bereikbaarheid.elements import get_elements
from bereikbaarheid.isochrones import get_isochrones
from bereikbaarheid.isochrones.serializer import IsochronesSerializer
from bereikbaarheid.permits import get_permits
from bereikbaarheid.permits.serializers import PermitSerializer
from bereikbaarheid.prohibitory import get_prohibitory
from bereikbaarheid.prohibitory.serializers import ProhibitorySerializer
from bereikbaarheid.sections import get_sections
from bereikbaarheid.traffic_signs import get_traffic_signs
from bereikbaarheid.traffic_signs.serializers import TrafficSignsSerializer
from bereikbaarheid.wrapper import extract_parameters, geo_json_response, validate_data


class BollardsView(View):
    """
    return Bollards with and without params
    """

    @geo_json_response
    def handle(self, request, data: dict, *args, **kwargs):
        return get_bollards(data)

    def get(self, request, *args, **kwargs):
        try:
            _params = extract_parameters(request)

            if _params:
                # if request with params -> validation:
                serialized_data = BollardsSerializer().load(_params)
                return self.handle(request, serialized_data)
            else:
                return self.handle(request, None)

        except ValidationError as err:
            return JsonResponse(status=400, data=err.messages)
        except json.JSONDecodeError as e:
            return JsonResponse(status=400, data={"error": str(e)})

    @validate_data(BollardsSerializer)
    def post(self, request: HttpRequest, serialized_data: dict, *args, **kwargs):
        return self.handle(request, serialized_data)


class TrafficSignsView(View):
    """
    Return the traffic signs locations based on the parameters
    """

    @geo_json_response
    def handle(self, request, data: dict, *args, **kwargs):
        return get_traffic_signs(data)

    @validate_data(TrafficSignsSerializer)
    def get(self, request, serialized_data: dict, *args, **kwargs):
        return self.handle(request, serialized_data)

    @validate_data(TrafficSignsSerializer)
    def post(self, request: HttpRequest, serialized_data: dict, *args, **kwargs):
        return self.handle(request, serialized_data)


class PermitsView(View):
    """
    Return the permits based on location and vehicle properties
    """

    def handle(self, request, data: dict, *args, **kwargs):
        return JsonResponse(
            status=200,
            data={
                "data": get_permits(data),
            },
        )

    @validate_data(PermitSerializer)
    def get(self, request, serialized_data: dict, *args, **kwargs):
        return self.handle(request, serialized_data)

    @validate_data(PermitSerializer)
    def post(self, request: HttpRequest, serialized_data: dict, *args, **kwargs):
        return self.handle(request, serialized_data)


class ProhibitorView(View):
    """
    Return prohibitory roads
    """

    @geo_json_response
    def handle(self, request, data: dict, *args, **kwargs):
        return get_prohibitory(data)

    @validate_data(ProhibitorySerializer)
    def get(self, request, serialized_data: dict, *args, **kwargs):
        return self.handle(request, serialized_data)

    @validate_data(ProhibitorySerializer)
    def post(self, request: HttpRequest, serialized_data: dict, *args, **kwargs):
        return self.handle(request, serialized_data)


class ElementsView(View):
    """
    Return roads based on the id
    """

    @geo_json_response
    def handle(self, request, element_id: int, *args, **kwargs):
        return get_elements(element_id)

    def get(self, request, element_id: int, *args, **kwargs):
        return self.handle(request, element_id)


class IsochronesView(View):
    """
    Return Isochrones
    """

    @geo_json_response
    def handle(self, request, data: dict, *args, **kwargs):
        return get_isochrones(data)

    @validate_data(IsochronesSerializer)
    def get(self, request, serialized_data: dict, *args, **kwargs):
        return self.handle(request, serialized_data)

    @validate_data(IsochronesSerializer)
    def post(self, request: HttpRequest, serialized_data: dict, *args, **kwargs):
        return self.handle(request, serialized_data)


class SectionsView(View):
    @geo_json_response
    def get(self, request, *args, **kwargs):
        return get_sections()
