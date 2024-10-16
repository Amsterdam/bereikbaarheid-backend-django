import json

from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt


def permissiondenied403(request):
    raise PermissionDenied


@csrf_exempt
def csp_report(request):
    if request.method == "POST":
        report = json.loads(request.body.decode("utf-8"))
        print(report)  # Of sla het rapport ergens op, zoals in een database
        return JsonResponse({"status": "ok"})
    return JsonResponse({"status": "method not allowed"}, status=405)
