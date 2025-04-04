from import_export.resources import ModelResource

from bereikbaarheid.models import Lastbeperking
from bereikbaarheid.resources.utils import (
    clean_dataset_headers,
    convert_str,
    refresh_materialized,
)


class LastbeperkingResource(ModelResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "linknr": "link_nr",
            "lastbeperking in kg": "lastbeperking_in_kg",
        }

        dataset.headers = clean_dataset_headers(dataset.headers, col_mapping)

    def before_import_row(self, row, **kwargs):
        if row["lastbeperking_in_kg"] == "NULL":
            row["lastbeperking_in_kg"] = None

        row["lastbeperking_in_kg"] = convert_str(row["lastbeperking_in_kg"], "float")

    def skip_row(self, instance, original, row, import_validation_errors=None):
        if not row["lastbeperking_in_kg"]:
            return True

        return super().skip_row(instance, original, row, import_validation_errors)

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
        model = Lastbeperking
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("link_nr",)
