import json
import urllib

from django.http import HttpRequest, JsonResponse
from marshmallow import ValidationError


def fix_traffic_sign_categories(request) -> dict:
    """
    This is an edge case because array parameters for this field are send as as multiple parameters:
    Example: 'trafficSignCategories=prohibition&trafficSignCategories=prohibition with exception'
    This won't work with the current parsing of the values
    TODO:: Remove this function when the frontend is switched to using the POST requests
    :param request:
    :return:
    """
    values = dict(urllib.parse.parse_qs(request.META["QUERY_STRING"]))
    for key, value in values.items():
        if "trafficSignCategories" in key:
            continue
        try:
            values[key] = value[0]
        except (ValueError, KeyError):
            continue
    return values


def extract_parameters(request: HttpRequest) -> dict:
    """
    Extract the parameters from either a get or post request
    and transform them to a dict
    :param request:
    :return:
    """
    if request.META["REQUEST_METHOD"] == "GET":
        if "trafficSignCategories" in request.META["QUERY_STRING"]:
            return fix_traffic_sign_categories(request)
        else:
            return dict(urllib.parse.parse_qsl(request.META["QUERY_STRING"]))
    else:
        return json.loads(request.body)


def validate_data(serializer):
    """
    Validate the incoming data through the selected serializer and validate the input.
    On valid it will pass through the validate data
    On invalid it will return a 400 Http with the error message
    :param serializer:
    :return:
    """
    def decorator(func):
        def wrapper(view, request, *args, **kwargs):
            try:
                data = serializer().load(extract_parameters(request))
                kwargs["serialized_data"] = data
                return func(view, request, *args, **kwargs)
            except ValidationError as err:
                return JsonResponse(status=400, data=err.messages)
            except json.JSONDecodeError as e:
                return JsonResponse(status=400, data={"error": str(e)})
        return wrapper

    return decorator


def geo_json_response(func):
    """
    Wrap any dict into a geojson format and return it as a json response
    :param func:
    :return:
    """

    def wrapped(*args, **kwargs):
        return JsonResponse(
            status=200,
            data={"features": func(*args, **kwargs), "type": "FeatureCollection"},
        )

    return wrapped
