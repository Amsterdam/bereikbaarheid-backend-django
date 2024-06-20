from import_export.resources import ModelResource

from bereikbaarheid.models import VerkeersTelling
from bereikbaarheid.resources.utils import clean_dataset_headers


class VerkeersTellingResource(ModelResource):
    def before_import(self, dataset, **kwargs):
        col_mapping = {
            "volgnummer": "volg_nummer",
            "latitude": "lat",
            "longitude": "lon",
            "vma_linknr": "link_nr",
            "telpuntnaam": "telpunt_naam",
            "meetmethode": "meet_methode",
        }

        dataset.headers = clean_dataset_headers(dataset.headers, col_mapping)

    class Meta:
        model = VerkeersTelling
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("volg_nummer",)
