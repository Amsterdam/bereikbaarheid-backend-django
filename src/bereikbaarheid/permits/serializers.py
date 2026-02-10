from marshmallow import Schema, fields, post_load, validate, validates

from bereikbaarheid.validation import (
    allowed_vehicle_types,
    bbox_adam,
    is_bus,
    is_company_car,
    voertuig,
)


class PermitSerializer(Schema):
    lat = fields.Float(
        required=True,
        validate=[validate.Range(min=bbox_adam["lat"]["min"], max=bbox_adam["lat"]["max"])],
    )

    lon = fields.Float(
        required=True,
        validate=[validate.Range(min=bbox_adam["lon"]["min"], max=bbox_adam["lon"]["max"])],
    )

    permit_zone_milieu = fields.Boolean(required=True, data_key="permitLowEmissionZone")
    permit_zone_7_5 = fields.Boolean(required=True, data_key="permitZzv")

    aslast_gewicht = fields.Integer(
        required=True,
        data_key="vehicleAxleWeight",
        validate=[
            validate.Range(
                min=voertuig["aslast_gewicht"]["min"],
                max=voertuig["aslast_gewicht"]["max"],
            )
        ],
    )

    aanhanger = fields.Boolean(required=True, data_key="vehicleHasTrailer")

    hoogte = fields.Float(
        required=True,
        data_key="vehicleHeight",
        validate=[
            validate.Range(
                min=voertuig["hoogte"]["min"],
                max=voertuig["hoogte"]["max"],
                min_inclusive=False,
            )
        ],
    )

    lengte = fields.Float(
        required=True,
        data_key="vehicleLength",
        validate=[validate.Range(min=voertuig["lengte"]["min"], max=voertuig["lengte"]["max"])],
    )

    breedte = fields.Float(
        required=True,
        data_key="vehicleWidth",
        validate=[validate.Range(min=voertuig["breedte"]["min"], max=voertuig["breedte"]["max"])],
    )

    max_massa = fields.Integer(
        required=True,
        data_key="vehicleMaxAllowedWeight",
        validate=[
            validate.Range(
                min=voertuig["maximale_toegestaande_gewicht"]["min"],
                max=voertuig["maximale_toegestaande_gewicht"]["max"],
            )
        ],
    )

    totaal_gewicht = fields.Integer(
        required=True,
        data_key="vehicleTotalWeight",
        validate=[
            validate.Range(
                min=voertuig["totaal_gewicht"]["min"],
                max=voertuig["totaal_gewicht"]["max"],
            )
        ],
    )

    voertuig_type = fields.String(required=True, data_key="vehicleType")

    @validates("voertuig_type")
    def allowed_vehicle_types(self, value: str, data_key: str) -> None:
        allowed_vehicle_types(value)

    @post_load
    def voertuigs_type(self, data: dict, **kwargs: dict) -> dict:
        """
        Post load to check the vehicle type to see if it is a "bedrijfsauto" or a bus
        Removes the "voertuig_type" key from the data
        :see: permit raw_query
        :param data:
        :param kwargs:
        :return:
        """
        vehicle_type = data.pop("voertuig_type", "")
        data["bedrijfsauto"] = is_company_car(vehicle_type)
        data["bus"] = is_bus(vehicle_type)
        return data
