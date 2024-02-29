from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from main.view_403 import permissiondenied403

from . import auth

urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [
    path(settings.API_PATH, include("bereikbaarheid.urls")),
    path(settings.API_PATH, include("touringcar.urls")),
    path("status/", include("health.urls")),
    path("403/", permissiondenied403),
]

if settings.ADMIN_ENABLED:
    urlpatterns.extend(
        [
            path(settings.ADMIN_PATH + "login/", auth.oidc_login),
            path(settings.ADMIN_PATH + "oidc/", include("mozilla_django_oidc.urls")),
            path(settings.ADMIN_PATH, admin.site.urls),
        ]
    )
