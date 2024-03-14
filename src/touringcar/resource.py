from import_export.resources import ModelResource

from touringcar.models import Bericht


class BerichtResource(ModelResource):
    def before_import(self, dataset, using_transactions, dry_run, **kwargs):
        col_mapping = {
            "location_lat": "lat",
            "location_lng": "lon",
        }

        # all lower
        dataset.headers = [x.strip().lower() for x in dataset.headers]
        # mapping of the model.py columnnames
        dataset.headers = [col_mapping.get(item, item) for item in dataset.headers]

        # trim leading and trailing spaces
        title_clean = [ x.strip() for x in dataset["title"]]
        del dataset["title"]
        dataset.append_col( title_clean, header="title")

    class Meta:
        model = Bericht
        skip_unchanged = True
        report_skipped = True
        exclude = ("id", "created_at", "updated_at")
        import_id_fields = ("title", "startdate", "enddate")
