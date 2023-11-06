from import_export.resources import ModelResource

from bereikbaarheid.models import Stremming
from bereikbaarheid.resources.utils import convert_to_date


class StremmingResource(ModelResource):
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        col_mapping = {
            "vma-linknr": "link_nr",
            "vma_linknr": "link_nr",
            "opmerk/beschrijving/": "opmerking",
            "wior_nr": "kenmerk",
            "gsu": "start_date",
            "geu": "end_date",
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]

    def before_import_row(self, row, row_number=None, **kwargs):
        row["start_date"] = convert_to_date(row["start_date"])
        row["end_date"] = convert_to_date(row["end_date"])

    class Meta:
        model = Stremming
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = (
            "link_nr",
            "start_date",
            "end_date",
            "werkzaamheden",
        )
