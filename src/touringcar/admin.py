from django import forms
from django.contrib import admin
from import_export.tmp_storages import CacheStorage
from leaflet.admin import LeafletGeoAdminMixin

from bereikbaarheid.admin import ImportExportFormatsMixin, ImportMixin
from bereikbaarheid.resources.utils import GEOJSON
from touringcar.models import Bericht, Doorrijhoogte, Halte, Parkeerplaats
from touringcar.resource import (
    BerichtResource,
    DoorrijhoogteResource,
    HalteResource,
    ParkeerplaatsResource,
)


class BerichtenForm(forms.ModelForm):
    class Meta:
        widgets = {
            "title": forms.TextInput(attrs={"size": "80"}),
            "title_en": forms.TextInput(attrs={"size": "80"}),
            "title_fr": forms.TextInput(attrs={"size": "80"}),
            "title_de": forms.TextInput(attrs={"size": "80"}),
            "title_es": forms.TextInput(attrs={"size": "80"}),
        }


@admin.register(Bericht)
class BerichtAdmin(ImportExportFormatsMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    form = BerichtenForm
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
    ordering = ("-enddate",)
    search_help_text = "zoek naar trefwoord in titel"
    search_fields = ["title"]

    # ordering on admin page touringcar
    fieldsets = [
        (
            None,
            {
                "fields": [
                    "title",
                    "body",
                    "advice",
                    "startdate",
                    "enddate",
                    "category",
                    "link",
                    "image_url",
                    "important",
                    "is_live",
                    "lat",
                    "lon",
                    "geometry",
                ],
            },
        ),
        (
            "Vertaalvelden (optioneel)",
            {
                "classes": ["collapse"],
                "fields": [
                    "title_en",
                    "body_en",
                    "advice_en",
                    "title_fr",
                    "body_fr",
                    "advice_fr",
                    "title_de",
                    "body_de",
                    "advice_de",
                    "title_es",
                    "body_es",
                    "advice_es",
                ],
            },
        ),
    ]


@admin.register(Halte)
class HalteAdmin(ImportMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    tmp_storage_class = CacheStorage
    readonly_fields = ["code"]
    list_display = [
        "name",
        "code",
        "location",
        "capacity",
        "created_at",
        "updated_at",
    ]
    list_filter = ["capacity", "created_at", "updated_at"]
    resource_classes = [HalteResource]
    ordering = ("code",)
    search_help_text = "zoek naar trefwoord in name"
    search_fields = ["name"]

    def get_import_formats(self):
        """Returns available import formats."""
        return [GEOJSON]


@admin.register(Parkeerplaats)
class ParkeerplaatsAdmin(ImportMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    tmp_storage_class = CacheStorage
    readonly_fields = ["code"]
    list_display = [
        "name",
        "code",
        "location",
        "capacity",
        "created_at",
        "updated_at",
    ]
    list_filter = ["capacity", "created_at", "updated_at"]
    resource_classes = [ParkeerplaatsResource]
    ordering = ("code",)
    search_help_text = "zoek naar trefwoord in name"
    search_fields = ["name"]

    def get_import_formats(self):
        """Returns available import formats."""
        return [GEOJSON]


@admin.register(Doorrijhoogte)
class ParkeerplaatsAdmin(ImportMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    tmp_storage_class = CacheStorage
    list_display = [
        "name",
        "id",
        "maxheight",
        "created_at",
        "updated_at",
    ]
    list_filter = ["maxheight", "created_at", "updated_at"]
    resource_classes = [DoorrijhoogteResource]
    ordering = ("name", "-id")
    search_help_text = "zoek naar trefwoord in name"
    search_fields = ["name"]

    def get_import_formats(self):
        """Returns available import formats."""
        return [GEOJSON]
