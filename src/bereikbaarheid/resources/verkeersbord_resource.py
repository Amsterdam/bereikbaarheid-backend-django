from django.contrib.gis.geos import GEOSGeometry
from import_export.resources import ModelResource

from bereikbaarheid.models import VerkeersBord
from bereikbaarheid.resources.utils import clean_dataset_headers, refresh_materialized


class VerkeersBordResource(ModelResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "script_linknr": "link_nr",
            "rvv-modelnummer": "rvv_modelnummer",
            "link_gevalideerd1": "link_gevalideerd",
            "onderbord tekst": "onderbord_tekst",
            "x-coordinaat": "rd_x",
            "y-coordinaat": "rd_y",
            "link_gevalideerd2": "link_validated_2",
        }

        dataset.headers = clean_dataset_headers(dataset.headers, col_mapping)

    def before_import_row(self, row, **kwargs):
        if row["tekst_waarde"] == "NULL":
            row["tekst_waarde"] = ""

        row["geometry"] = GEOSGeometry(
            "POINT(%s %s)" % (row["rd_x"], row["rd_y"]), srid=28992
        )

    def before_save_instance(self, instance, row, **kwargs):
        # import_export Version 4 change: param dry-run passed in kwargs
        # during 'confirm' step, dry_run is True
        instance.dry_run = kwargs.get("dry_run", False)

    def after_import(self, dataset, result, **kwargs):
        # import_export Version 4 change: param dry-run passed in kwargs
        # refresh materialized vieuws when dry_run = False
        dry_run = kwargs.get("dry_run", False)
        if not dry_run:
            refresh_materialized("bereikbaarheid_out_vma_undirected")
            refresh_materialized("bereikbaarheid_out_vma_directed")
            refresh_materialized("bereikbaarheid_out_vma_node")

    class Meta:
        model = VerkeersBord
        skip_unchanged = True
        report_skipped = False
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("bord_id",)
