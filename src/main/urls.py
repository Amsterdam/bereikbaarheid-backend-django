from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from . import auth

urlpatterns = static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += [
    path(settings.API_PATH, include("bereikbaarheid.urls")),
    path("status/", include("health.urls")),
]

if settings.ADMIN_ENABLED:
    urlpatterns.extend(
        [
            path(settings.ADMIN_PATH + "login/", auth.oidc_login),
            path(settings.ADMIN_PATH + "oidc/", include("mozilla_django_oidc.urls")),
            path(settings.ADMIN_PATH, admin.site.urls),
        ]
    )
