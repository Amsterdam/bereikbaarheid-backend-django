from import_export.resources import ModelResource

from bereikbaarheid.models import VerkeersPaal
from bereikbaarheid.resources.utils import (
    clean_dataset_headers,
    remove_chars_from_value,
)


class VerkeersPaalResource(ModelResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "linknr": "link_nr",
            "paalnummer": "paal_nr",
        }

        dataset.headers = clean_dataset_headers(dataset.headers, col_mapping)

        # remove [] or {} of array by import
        dataset.append_col(
            [remove_chars_from_value(x, "[]{}") for x in dataset["dagen"]],
            header="dagen",
        )

    def before_import_row(self, row, **kwargs):
        if row["paal_nr"] == "None":
            row["paal_nr"] = ""

    class Meta:
        model = VerkeersPaal
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("link_nr", "dagen", "begin_tijd", "eind_tijd", "geometry")
