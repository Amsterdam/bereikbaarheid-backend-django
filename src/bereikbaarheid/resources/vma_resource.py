from django.contrib.gis.geos import GEOSGeometry
from import_export.instance_loaders import CachedInstanceLoader
from import_export.resources import ModelResource

from bereikbaarheid.models import Vma
from bereikbaarheid.resources.utils import (
    clean_dataset_headers,
    refresh_materialized,
    truncate,
)


class VmaResource(ModelResource):
    def before_import(self, dataset, **kwargs):
        # import_export Version 4 change: param dry-run passed in kwargs
        col_mapping = {
            "linknr": "link_nr",
        }

        dataset.headers = clean_dataset_headers(dataset.headers, col_mapping)
        # during 'confirm' step, dry_run is True -> in VmaAdmin import_action is dry_run set on False
        dry_run = kwargs.get("dry_run", False)
        if not dry_run:
            truncate(Vma)

    def before_import_row(self, row, **kwargs):
        row["geom"] = GEOSGeometry(row["geom"], srid=28992)

    def after_import(self, dataset, result, **kwargs):
        # import_export Version 4 change: param dry-run passed in kwargs
        # refresh materialized vieuws when dry_run = False
        dry_run = kwargs.get("dry_run", False)
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
