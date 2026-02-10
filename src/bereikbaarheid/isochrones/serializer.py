from marshmallow import Schema, fields, validate

from bereikbaarheid.validation import bbox_adam


class IsochronesSerializer(Schema):
    lat = fields.Float(
        required=True,
        validate=[validate.Range(min=bbox_adam["lat"]["min"], max=bbox_adam["lat"]["max"])],
    )

    lon = fields.Float(
        required=True,
        validate=[validate.Range(min=bbox_adam["lon"]["min"], max=bbox_adam["lon"]["max"])],
    )
