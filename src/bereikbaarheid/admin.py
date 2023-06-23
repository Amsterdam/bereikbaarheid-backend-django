import json
import warnings

from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.template.response import TemplateResponse
from import_export.admin import ImportExportMixin, ImportMixin
from import_export.formats import base_formats
from import_export.forms import ImportExportFormBase
from leaflet.admin import LeafletGeoAdminMixin

from bereikbaarheid.models import (
    Gebieden,
    Lastbeperking,
    Stremmingen,
    VenstertijdWegen,
    VerkeersBorden,
    VerkeersTellingen,
    Verrijking,
    Vma,
)
from bereikbaarheid.resources.gebieden_resource import GebiedenResource
from bereikbaarheid.resources.lastbeperking_resource import LastbeperkingResource
from bereikbaarheid.resources.stremmingen_resource import StremmingenResource
from bereikbaarheid.resources.utils import GEOJSON, SCSV
from bereikbaarheid.resources.venstertijdwegen_resource import VenstertijdWegenResource
from bereikbaarheid.resources.verkeersborden_resource import VerkeersBordenResource
from bereikbaarheid.resources.verkeerstellingen_resource import (
    VerkeersTellingenResource,
)
from bereikbaarheid.resources.verrijking_resource import VerrijkingResource
from bereikbaarheid.resources.vma_resource import VmaResource


@admin.register(VenstertijdWegen)
class VenstertijdWegenAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
        "link_nr",
        "name",
        "verkeersbord",
        "dagen",
        "begin_tijd",
        "eind_tijd",
    ]
    list_filter = ["verkeersbord", "dagen", "begin_tijd", "eind_tijd"]
    resource_classes = [VenstertijdWegenResource]

    def get_import_formats(self):
        """Returns available import formats."""
        formats = [SCSV, base_formats.XLSX]
        return formats


@admin.register(Gebieden)
class GebiedenAdmin(ImportMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    list_display = ["xid"]
    resource_classes = [GebiedenResource]
    modifiable = False  # Make the leaflet map read-only

    def get_import_formats(self):
        """Returns available import formats."""
        return [GEOJSON]

    # disable add functionality
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Lastbeperking)
class LastbeperkingAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["p_id", "link_nr", "lastbeperking_in_kg"]
    resource_classes = [LastbeperkingResource]


@admin.register(Stremmingen)
class StremmingenAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["p_id", "link_nr", "werkzaamheden", "kenmerk"]
    list_filter = ["start_date", "end_date"]
    resource_classes = [StremmingenResource]


@admin.register(VerkeersBorden)
class VerkeersBordenAdmin(ImportExportMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    list_display = ["p_id", "bord_id", "geldigheid", "rvv_modelnummer"]
    list_filter = ["geldigheid", "rvv_modelnummer"]
    resource_classes = [VerkeersBordenResource]
    modifiable = False  # Make the leaflet map read-only

    # disable add functionality
    def has_add_permission(self, request):
        return False


@admin.register(VerkeersTellingen)
class VerkeersTellingenAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = ["volg_nummer", "telpunt_naam", "link_nr", "jaar"]
    list_filter = ["jaar", "type_verkeer", "meet_methode"]
    resource_classes = [VerkeersTellingenResource]


@admin.register(Verrijking)
class VerrijkingAdmin(ImportExportMixin, admin.ModelAdmin):
    list_display = [
        "p_id",
        "link_nr",
        "binnen_amsterdam",
        "zone_zwaar_verkeer_bus",
        "frc",
    ]
    list_filter = ["binnen_amsterdam", "wegcategorie_actueel"]
    resource_classes = [VerrijkingResource]

    # disable add functionality
    def has_add_permission(self, request):
        return False


@admin.register(Vma)
class VmaAdmin(ImportMixin, LeafletGeoAdminMixin, admin.ModelAdmin):
    list_display = ["gid", "link_nr", "name"]
    resource_classes = [VmaResource]
    modifiable = False  # Make the leaflet map read-only
    skip_admin_log = True

    def get_import_formats(self):
        """Returns available import formats."""
        return [GEOJSON]

    # This will help you to disbale add functionality
    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def import_action(self, request, *args, **kwargs):
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
        if getattr(self.get_form_kwargs, "is_original", False):
            # Use new API
            import_form = self.create_import_form(request)
        else:
            form_class = self.get_import_form_class(request)
            form_kwargs = self.get_form_kwargs(form_class, *args, **kwargs)

            if issubclass(form_class, ImportExportFormBase):
                import_form = form_class(
                    import_formats,
                    self.get_import_resource_classes(),
                    request.POST or None,
                    request.FILES or None,
                    **form_kwargs
                )
            else:
                warnings.warn(
                    "The ImportForm class must inherit from ImportExportFormBase, "
                    "this is needed for multiple resource classes to work properly. ",
                    category=DeprecationWarning,
                )
                import_form = form_class(
                    import_formats,
                    request.POST or None,
                    request.FILES or None,
                    **form_kwargs
                )

        resources = list()
        if request.POST and import_form.is_valid():
            input_format = import_formats[
                int(import_form.cleaned_data["input_format"])
            ]()
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

                print(type(data))

                return data

            # This setting means we are going to skip the import confirmation step.
            if True:
                # Go ahead and process the file for import in a transaction
                # If there are any errors, we roll back the transaction.
                # rollback_on_validation_errors is set to True so that we rollback on
                # validation errors. If this is not done validation errors would be
                # silently skipped.

                data = _read_data(import_file)

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
                        **kwargs
                    )
                    if not result.has_errors() and not result.has_validation_errors():
                        return self.process_result(result, request)
                    else:
                        context["result"] = result

        else:
            res_kwargs = self.get_import_resource_kwargs(
                request, form=import_form, *args, **kwargs
            )
            resource_classes = self.get_import_resource_classes()
            resources = [
                resource_class(**res_kwargs) for resource_class in resource_classes
            ]

        context.update(self.admin_site.each_context(request))

        context["title"] = _("Import")
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
