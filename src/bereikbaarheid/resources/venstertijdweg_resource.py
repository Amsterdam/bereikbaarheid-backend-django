from import_export.resources import ModelResource

from bereikbaarheid.models import VenstertijdWeg
from bereikbaarheid.resources.utils import (
    clean_dataset_headers,
    convert_to_time,
    remove_chars_from_value,
)


class VenstertijdWegResource(ModelResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "linknr": "link_nr",
        }

        dataset.headers = clean_dataset_headers(dataset.headers, col_mapping)

        # remove [] or {} of array by import
        dataset.append_col(
            [remove_chars_from_value(x, "[]{}") for x in dataset["dagen"]],
            header="dagen",
        )

    def before_import_row(self, row, **kwargs):
        row["begin_tijd"] = convert_to_time(row["begin_tijd"])
        row["eind_tijd"] = convert_to_time(row["eind_tijd"])

    def skip_row(self, instance, original, row, import_validation_errors=None):
        # skip ontbrekend id in import file = legeregels in csv
        if not row["link_nr"]:
            return True

        return super().skip_row(instance, original, row, import_validation_errors)

    class Meta:
        model = VenstertijdWeg
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = (
            "link_nr",
            "name",
            "e_type",
            "verkeersbord",
            "dagen",
            "begin_tijd",
            "eind_tijd",
        )
