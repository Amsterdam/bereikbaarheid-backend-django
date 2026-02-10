import json

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from import_export.admin import (
    ImportExportActionModelAdmin,
    ImportExportMixin,
    ImportMixin,
)
from import_export.formats import base_formats
from import_export.tmp_storages import CacheStorage
from leaflet.admin import LeafletGeoAdminMixin

from bereikbaarheid.models import (
    Gebied,
    Lastbeperking,
    VenstertijdWeg,
    VerkeersBord,
    VerkeersPaal,
    VerkeersTelling,
    Verrijking,
    Vma,
)
from bereikbaarheid.resources.gebied_resource import GebiedResource
from bereikbaarheid.resources.lastbeperking_resource import LastbeperkingResource
from bereikbaarheid.resources.utils import GEOJSON, SCSV
from bereikbaarheid.resources.venstertijdweg_resource import VenstertijdWegResource
from bereikbaarheid.resources.verkeersbord_resource import VerkeersBordResource
from bereikbaarheid.resources.verkeerspaal_resource import VerkeersPaalResource
from bereikbaarheid.resources.verkeerstelling_resource import VerkeersTellingResource
from bereikbaarheid.resources.verrijking_resource import VerrijkingResource
from bereikbaarheid.resources.vma_resource import VmaResource

from .validation import days_of_the_week_abbreviated


class ArrayDagenListFilter(admin.SimpleListFilter):
    """This is a list filter based on the values
    from a model's `keywords` ArrayField."""

    title = "dagen"

    # Parameter for the filter that will be used in the URL query.
    parameter_name = "dagen"

    def lookups(self, request, model_admin):
        """
        Returns a list of tuples.
        (lookup_value, human-readable value). These
        appear in the admin's right sidebar
        """
        return [(d, d) for d in days_of_the_week_abbreviated]

    def queryset(self, request, queryset):
        """
        Returns the filtered queryset based on the value
        provided in the query string and retrievable via
        `self.value()`.
        """
        lookup_value = self.value()  # The clicked keyword. It can be None!
        if lookup_value:
            # the __contains lookup expects a list, so...
            queryset = queryset.filter(dagen__contains=[lookup_value])
        return queryset


class ImportExportFormatsMixin(ImportExportMixin, ImportExportActionModelAdmin):
    """overwrites the standard get_import_formats and get_export_formats from the ImportExportMixin"""

    def get_import_formats(self):
        """Returns available import formats."""
        formats = [SCSV, base_formats.XLSX, base_formats.CSV]
        return formats

    def get_export_formats(self):
        """Returns available import formats."""
        formats = [SCSV, base_formats.XLSX, base_formats.CSV, base_formats.JSON]
        return formats


@admin.register(VenstertijdWeg)
class VenstertijdWegAdmin(ImportExportFormatsMixin, admin.ModelAdmin):
    tmp_storage_class = CacheStorage
    list_display = [
        "link_nr",
        "name",
        "verkeersbord",
        "dagen",
        "begin_tijd",
        "eind_tijd",
        "created_at",
        "updated_at",
    ]
    list_filter = [ArrayDagenListFilter, "created_at", "updated_at"]
    resource_classes = [VenstertijdWegResource]


@admin.register(Gebied)
class GebiedAdmin(ImportMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    map_template = "leaflet/admin/custom_widget.html"

    tmp_storage_class = CacheStorage
    list_display = ["id"]
    resource_classes = [GebiedResource]
    modifiable = False  # Make the leaflet map read-only

    def get_import_formats(self):
        """Returns available import formats."""
        return [GEOJSON]

    # disable add functionality
    def has_add_permission(self, request):
        return False


@admin.register(Lastbeperking)
class LastbeperkingAdmin(ImportExportFormatsMixin, admin.ModelAdmin):
    tmp_storage_class = CacheStorage
    list_display = ["id", "link_nr", "lastbeperking_in_kg", "created_at", "updated_at"]
    list_filter = ["created_at", "updated_at"]
    resource_classes = [LastbeperkingResource]


@admin.register(VerkeersBord)
class VerkeersBordAdmin(ImportExportFormatsMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    map_template = "leaflet/admin/custom_widget.html"

    tmp_storage_class = CacheStorage
    list_display = [
        "id",
        "bord_id",
        "geldigheid",
        "rvv_modelnummer",
        "created_at",
        "updated_at",
    ]
    list_filter = ["geldigheid", "rvv_modelnummer", "created_at", "updated_at"]
    resource_classes = [VerkeersBordResource]
    modifiable = False  # Make the leaflet map read-only
    ordering = ("bord_id",)
    search_help_text = "search by bord id"
    search_fields = ["bord_id"]


@admin.register(VerkeersPaal)
class VerkeersPalenAdmin(ImportExportFormatsMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    map_template = "leaflet/admin/custom_widget.html"

    tmp_storage_class = CacheStorage
    list_display = [
        "paal_nr",
        "link_nr",
        "standplaats",
        "dagen",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "type",
        "toegangssysteem",
        ArrayDagenListFilter,
        "beheerorganisatie",
        "verkeersbord",
        "jaar_aanleg",
        "created_at",
        "updated_at",
    ]
    resource_classes = [VerkeersPaalResource]
    modifiable = False  # Make the leaflet map read-only
    ordering = ["link_nr", "standplaats"]

    # disable add functionality
    def has_add_permission(self, request):
        return False


@admin.register(VerkeersTelling)
class VerkeersTellingAdmin(ImportExportFormatsMixin, admin.ModelAdmin):
    tmp_storage_class = CacheStorage
    list_display = [
        "volg_nummer",
        "telpunt_naam",
        "link_nr",
        "jaar",
        "created_at",
        "updated_at",
    ]
    list_filter = ["jaar", "type_verkeer", "meet_methode", "created_at", "updated_at"]
    resource_classes = [VerkeersTellingResource]


@admin.register(Verrijking)
class VerrijkingAdmin(ImportExportFormatsMixin, admin.ModelAdmin):
    tmp_storage_class = CacheStorage
    list_display = [
        "id",
        "link_nr",
        "binnen_amsterdam",
        "binnen_polygoon_awb",
        "milieuzone",
        "zone_zwaar_verkeer_bus",
        "zone_zwaar_verkeer_non_bus",
        "frc",
        "created_at",
        "updated_at",
    ]
    list_filter = [
        "binnen_amsterdam",
        "binnen_polygoon_awb",
        "milieuzone",
        "zone_zwaar_verkeer_bus",
        "zone_zwaar_verkeer_non_bus",
        "created_at",
        "updated_at",
    ]
    resource_classes = [VerrijkingResource]

    # disable add functionality
    def has_add_permission(self, request):
        return False


@admin.register(Vma)
class VmaAdmin(ImportMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    map_template = "leaflet/admin/custom_widget.html"

    tmp_storage_class = CacheStorage
    list_display = ["id", "link_nr", "name"]
    resource_classes = [VmaResource]
    modifiable = False  # Make the leaflet map read-only
    skip_admin_log = True

    def get_import_formats(self):
        """Returns available import formats."""
        return [GEOJSON, base_formats.CSV]

    # This will help you to disbale add functionality
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def import_action(self, request, *args, **kwargs):
        # import_export Version 4 major changes: code adjustment for this overwrite of import_action to keep working
        """
        This method is overwritten to battle the exponential growth of loading time when
        chuck loading a large GEOJSON-file. To keep the same behavior we had to import the whole
        method to not conflict with any other paths

        Perform a dry_run of the import to make sure the import will not
        result in errors.  If there are no errors, 'process_import' for the actual import.
        """
        if not self.has_import_permission(request):
            raise PermissionDenied

        context = self.get_import_context_data()

        import_formats = self.get_import_formats()
        import_form = self.create_import_form(request)
        resources = list()
        if request.POST and import_form.is_valid():
            input_format = import_formats[int(import_form.cleaned_data["format"])]()
            if not input_format.is_binary():
                input_format.encoding = self.from_encoding
            import_file = import_form.cleaned_data["import_file"]

            def _read_data(import_file) -> dict:
                """
                This part is overwritten because the original chunking of the file would
                have an exponential growth on loading time depending on the files size.
                It got changed to read it for each row and create our own geojson dataset.
                Which is then transformed in the custom dataframe loader(see: utils.GEOJSON)
                to transform it to a dataframe to be used by the import-export module
                """
                data = {
                    "type": "FeatureCollection",
                    "name": "NAME_PLACEHOLDER",
                    "crs": {
                        "type": "name",
                        "properties": {"name": "urn:ogc:def:crs:EPSG::28992"},
                    },
                    "features": [],
                }
                for line in import_file:
                    s_line = (
                        line.decode("utf-8").replace(",\n", "").replace("\n", "")
                    )  # remove ,\n and decode to string
                    if '"type": "Feature"' not in s_line:
                        continue
                    data["features"].append(json.loads(s_line))

                return data

            # This setting means we are going to skip the import confirmation step.
            if True:
                # Go ahead and process the file for import in a transaction
                # If there are any errors, we roll back the transaction.
                # rollback_on_validation_errors is set to True so that we rollback on
                # validation errors. If this is not done validation errors would be
                # silently skipped.

                if input_format.get_title() == "geojson":
                    data = _read_data(import_file)
                else:  # read other formats
                    data = bytes()
                    for chunk in import_file.chunks():
                        data += chunk

                try:
                    dataset = input_format.create_dataset(data)
                except Exception as e:
                    self.add_data_read_fail_error_to_form(import_form, e)
                if not import_form.errors:
                    result = self.process_dataset(
                        dataset,
                        import_form,
                        request,
                        *args,
                        raise_errors=False,
                        rollback_on_validation_errors=True,
                        **kwargs,
                    )
                    if not result.has_errors() and not result.has_validation_errors():
                        return self.process_result(result, request)
                    else:
                        context["result"] = result

        else:
            res_kwargs = self.get_import_resource_kwargs(request, form=import_form, **kwargs)
            resource_classes = self.get_import_resource_classes(request)
            resources = [resource_class(**res_kwargs) for resource_class in resource_classes]

        context.update(self.admin_site.each_context(request))

        context["title"] = "Import"
        context["form"] = import_form
        context["opts"] = self.model._meta
        context["media"] = self.media + import_form.media
        context["fields_list"] = [
            (
                resource.get_display_name(),
                [f.column_name for f in resource.get_user_visible_fields()],
            )
            for resource in resources
        ]

        request.current_app = self.admin_site.name
        return TemplateResponse(request, [self.import_template_name], context)
