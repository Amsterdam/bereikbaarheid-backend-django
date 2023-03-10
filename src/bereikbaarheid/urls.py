from django.urls import path
from django.views.generic import TemplateView

from .views import TrafficSignsView, PermitsView, ProhibitorView, ObstructionsView, \
    ElementsView, IsochronesView, SectionsView

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('v1/traffic-signs/', TrafficSignsView.as_view()),
    path('v1/permits/', PermitsView.as_view()),

    path('v1/road-obstructions/', ObstructionsView.as_view()),
    path('v1/road-elements/<int:element_id>/', ElementsView.as_view()),

    path('v1/road-sections/load-unload/', SectionsView.as_view()),

    path('v1/roads/prohibitory/', ProhibitorView.as_view()),
    path('v1/roads/isochrones/', IsochronesView.as_view()),

    path('swagger/openapi.yml', TemplateView.as_view(
            template_name='swagger/openapi.yml',
            extra_context={'schema_url': 'openapi-schema'}
    ), name='swagger-ui')
]
