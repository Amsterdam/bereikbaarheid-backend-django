from django import forms
from django.contrib import admin
from import_export.tmp_storages import CacheStorage
from leaflet.admin import LeafletGeoAdminMixin

from bereikbaarheid.admin import ImportExportFormatsMixin
from touringcar.model import Bericht
from touringcar.resource import BerichtResource


class BerichtenForm(forms.ModelForm): 
    class Meta:
        widgets = {
            'title': forms.TextInput(attrs={'size':'80'}),
            'title_en': forms.TextInput(attrs={'size':'80'}),
            'title_fr': forms.TextInput(attrs={'size':'80'}),
            'title_de': forms.TextInput(attrs={'size':'80'}),
            'title_es': forms.TextInput(attrs={'size':'80'}),
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

    # ordering on admin page touringcar
    fieldsets = [
        (
            None,
            {
                "fields": ["title", "body", "advice", "startdate", "enddate", "category", "link", "image_url", "important","is_live", "lat", "lon", "geometry"],
            },
        ),
        (
            "Vertaalvelden (optioneel)",
            {
                "classes": ["collapse"],
                "fields": ["title_en","body_en", "advice_en", "title_fr","body_fr", "advice_fr", "title_de","body_de", "advice_de","title_es","body_es", "advice_es"],
            },
        ),
    ]
