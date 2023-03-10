from import_export.resources import ModelResource

from bereikbaarheid.models import VenstertijdWegen
from bereikbaarheid.resources.utils import convert_to_time


class VenstertijdWegenResource(ModelResource):
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):

        col_mapping = {
            "linknr": "link_nr",
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]

    def before_import_row(self, row, row_number=None, **kwargs):

        row["begin_tijd"] = convert_to_time(row["begin_tijd"])
        row["eind_tijd"] = convert_to_time(row["eind_tijd"])

    def skip_row(self, instance, original, row, import_validation_errors=None):
        # skip ontbrekend id in import file = legeregels in csv
        if not row["link_nr"]:
            return True

        return super().skip_row(instance, original, row, import_validation_errors)

    class Meta:
        model = VenstertijdWegen
        skip_unchanged = True
        report_skipped = True
        exclude = ("id",)
        import_id_fields = (
            "link_nr",
            "name",
            "e_type",
            "verkeersbord",
            "dagen",
            "begin_tijd",
            "eind_tijd",
        )
