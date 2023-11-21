from django.contrib import admin
from import_export.tmp_storages import CacheStorage
from leaflet.admin import LeafletGeoAdminMixin

from bereikbaarheid.admin import ImportExportFormatsMixin
from touringcar.model import Bericht
from touringcar.resource import BerichtResource


@admin.register(Bericht)
class BerichtAdmin(ImportExportFormatsMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    tmp_storage_class = CacheStorage
    list_display = [
        "title",
        "startdate",
        "enddate",
        "is_live",
        "important",
        "link",
        "created_at",
        "updated_at",
    ]
    list_filter = ["startdate", "enddate", "is_live", "important", "updated_at"]
    resource_classes = [BerichtResource]