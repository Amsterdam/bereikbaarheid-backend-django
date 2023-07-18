from django.contrib.gis.geos import GEOSGeometry
from import_export.resources import ModelResource

from bereikbaarheid.models import Gebied
from bereikbaarheid.resources.utils import refresh_materialized


class GebiedResource(ModelResource):
    def before_import_row(self, row, row_number, **kwargs):
        row["geom"] = GEOSGeometry(str(row["geometry"]))

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        # refresh materialized vieuws when dry_run = False
        if not dry_run:
            refresh_materialized("bereikbaarheid_out_vma_undirected")
            refresh_materialized("bereikbaarheid_out_vma_directed")
            refresh_materialized("bereikbaarheid_out_vma_node")

    class Meta:
        model = Gebied
        exclude = ("id",)
        import_id_fields = ("geom",)
