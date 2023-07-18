from django.contrib.gis.geos import GEOSGeometry
from import_export.instance_loaders import CachedInstanceLoader
from import_export.resources import ModelResource

from bereikbaarheid.models import Vma
from bereikbaarheid.resources.utils import refresh_materialized, truncate


class VmaResource(ModelResource):
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        col_mapping = {
            "linknr": "link_nr",
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]

        # truncate table before import when dry_run = False
        if not dry_run:
            truncate(Vma)

    def before_import_row(self, row, row_number, **kwargs):
        row["geom"] = GEOSGeometry(row["geometry"], srid=28992)

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        # refresh materialized vieuws when dry_run = False
        if not dry_run:
            refresh_materialized("bereikbaarheid_out_vma_undirected")
            refresh_materialized("bereikbaarheid_out_vma_directed")
            refresh_materialized("bereikbaarheid_out_vma_node")

    class Meta:
        model = Vma
        exclude = ("id",)
        import_id_fields = ("link_nr",)
        fields = (
            "link_nr",
            "name",
            "direction",
            "length",
            "anode",
            "bnode",
            "wegtypeab",
            "wegtypeba",
            "speedab",
            "speedba",
            "wegtype_ab",
            "wegtype_ba",
            "geom",
        )
        instance_loader_class = CachedInstanceLoader
        use_bulk = True
        force_init_instance = True
        # skip_diff = True
