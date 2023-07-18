from import_export.resources import ModelResource

from bereikbaarheid.models import Verrijking
from bereikbaarheid.resources.utils import refresh_materialized


class VerrijkingResource(ModelResource):
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        col_mapping = {
            "linknr": "link_nr",
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]

    def after_import(self, dataset, result, using_transactions, dry_run, **kwargs):
        # refresh materialized vieuws when dry_run = False
        if not dry_run:
            refresh_materialized("bereikbaarheid_out_vma_undirected")
            refresh_materialized("bereikbaarheid_out_vma_directed")
            refresh_materialized("bereikbaarheid_out_vma_node")

    class Meta:
        model = Verrijking
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = ("link_nr",)
