from import_export.resources import ModelResource

from bereikbaarheid.models import Lastbeperking
from bereikbaarheid.resources.utils import convert_str, refresh_materialized


class LastbeperkingResource(ModelResource):
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        col_mapping = {
            "linknr": "link_nr",
            "lastbeperking in kg": "lastbeperking_in_kg",
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]

    def before_import_row(self, row, row_number=None, **kwargs):
        if row["lastbeperking_in_kg"] == "NULL":
            row["lastbeperking_in_kg"] = None

        row["lastbeperking_in_kg"] = convert_str(row["lastbeperking_in_kg"], "float")

    def skip_row(self, instance, original, row, import_validation_errors=None):
        if not row["lastbeperking_in_kg"]:
            return True

        return super().skip_row(instance, original, row, import_validation_errors)

    def before_save_instance(self, instance, using_transactions, dry_run):
        instance.dry_run = dry_run  # set a temporal flag for dry-run mode

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        # refresh materialized vieuws when dry_run = False
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
