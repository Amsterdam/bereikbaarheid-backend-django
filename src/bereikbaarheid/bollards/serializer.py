from marshmallow import Schema, ValidationError, fields, validate, validates_schema

from bereikbaarheid.validation import bbox_adam, days_of_the_week_abbreviated


class BollardsSerializer(Schema):
    day_of_the_week = fields.String(
        required=False,
        data_key="dayOfTheWeek",
        validate=validate.OneOf(days_of_the_week_abbreviated),
    )

    lat = fields.Float(
        required=True,
        validate=[validate.Range(min=bbox_adam["lat"]["min"], max=bbox_adam["lat"]["max"])],
    )

    lon = fields.Float(
        required=True,
        validate=[validate.Range(min=bbox_adam["lon"]["min"], max=bbox_adam["lon"]["max"])],
    )

    time_from = fields.Time(format="%H:%M", required=False, data_key="timeFrom")

    time_to = fields.Time(format="%H:%M", required=False, data_key="timeTo")

    @validates_schema
    def validate_dates(self, data, **kwargs):
        if not all(x in data for x in ["time_to", "time_from"]):
            return

        if data["time_to"] < data["time_from"]:
            raise ValidationError("timeTo must be later than timeFrom")

    @validates_schema
    def validate_field_dependencies(self, data, **kwargs):
        dependent_fields = ["day_of_the_week", "time_from", "time_to"]

        if any(x in data for x in dependent_fields):
            missing_fields = [f for f in dependent_fields if f not in data]

            if missing_fields:
                raise ValidationError(f"Missing fields: {', '.join(missing_fields)}")
