from import_export.instance_loaders import CachedInstanceLoader
from import_export.resources import ModelResource

from bereikbaarheid.models import Verrijking
from bereikbaarheid.resources.utils import clean_dataset_headers, refresh_materialized


class VerrijkingResource(ModelResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "linknr": "link_nr",
        }

        dataset.headers = clean_dataset_headers(dataset.headers, col_mapping)

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
        model = Verrijking
        skip_unchanged = True
        report_skipped = False
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("link_nr",)
        instance_loader_class = CachedInstanceLoader
        use_bulk = True
