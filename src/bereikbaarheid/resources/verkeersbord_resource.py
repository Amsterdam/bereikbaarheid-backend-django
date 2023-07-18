from datetime import datetime

from django.contrib.gis.geos import GEOSGeometry
from import_export.resources import ModelResource

from bereikbaarheid.models import VerkeersBord
from bereikbaarheid.resources.utils import refresh_materialized


class VerkeersBordResource(ModelResource):
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        col_mapping = {
            "script_linknr": "link_nr",
            "rvv-modelnummer": "rvv_modelnummer",
            "link_gevalideerd1": "link_gevalideerd",
            "onderbord tekst": "onderbord_tekst",
            "x-coordinaat": "rd_x",
            "y-coordinaat": "rd_y",
            "link_gevalideerd2": "link_validated_2",
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]

    def before_import_row(self, row, row_number=None, **kwargs):
        if row["tekst_waarde"] == "NULL":
            row["tekst_waarde"] = ""

        row["geometry"] = GEOSGeometry(
            "POINT(%s %s)" % (row["rd_x"], row["rd_y"]), srid=28992
        )

    def after_import_instance(self, instance, new, row_number=None, **kwargs):
        # set versie on now() @TODO kan ook via model.py versie = models.DateField(auto_now=True) wat heeft voorkeur?
        instance.versie = datetime.now()

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        # refresh materialized vieuws when dry_run = False
        if not dry_run:
            refresh_materialized("bereikbaarheid_out_vma_undirected")
            refresh_materialized("bereikbaarheid_out_vma_directed")
            refresh_materialized("bereikbaarheid_out_vma_node")

    class Meta:
        model = VerkeersBord
        skip_unchanged = True
        report_skipped = False
        exclude = ("id",)
        import_id_fields = ("bord_id",)
