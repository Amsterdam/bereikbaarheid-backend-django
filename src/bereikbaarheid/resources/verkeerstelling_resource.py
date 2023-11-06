from import_export.resources import ModelResource

from bereikbaarheid.models import VerkeersTelling


class VerkeersTellingResource(ModelResource):
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        col_mapping = {
            "volgnummer": "volg_nummer",
            "latitude": "lat",
            "longitude": "lon",
            "vma_linknr": "link_nr",
            "telpuntnaam": "telpunt_naam",
            "meetmethode": "meet_methode",
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]

    class Meta:
        model = VerkeersTelling
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("volg_nummer",)
