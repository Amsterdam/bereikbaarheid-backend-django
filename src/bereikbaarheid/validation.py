from marshmallow import ValidationError

# Constants used for validating API parameters
bbox_adam = {
    "lat": {"min": 52.2, "max": 52.47},
    "lon": {"min": 4.7, "max": 5.1},
}

days_of_the_week_abbreviated = ["ma", "di", "wo", "do", "vr", "za", "zo"]

# The vehicle parameters should be in sync with validation requirements
# for client-side forms (defined in javascript)
voertuig = {
    "aslast_gewicht": {"min": 0, "max": 12000},  # in kilograms
    "hoogte": {"min": 0, "max": 4},  # in meters
    "lengte": {"min": 0, "max": 22},  # in meters
    "maximale_toegestaande_gewicht": {"min": 0, "max": 60000},  # in kilograms
    "totaal_gewicht": {"min": 0, "max": 60000},  # in kilograms
    # vehicle types are equal to types defined by RDW
    # see https://opendata.rdw.nl/resource/9dze-d57m.json
    "types": ("Bedrijfsauto", "Bus", "Personenauto"),
    "breedte": {"min": 0, "max": 3},  # in meters
}


def allowed_vehicle_types(vehicle_type):
    """
    Checks allowed vehicle types.
    To be used in a marshmallow Schema
    Lowercase values are also allowed, because when preparing database
    query parameters the vehicle type is checked in the same way
    """
    if vehicle_type.casefold() not in map(str.casefold, voertuig["types"]):
        raise ValidationError("Moet één zijn van: " + ", ".join(voertuig["types"]))


def is_bus(vehicle_type: str) -> bool:
    return vehicle_type.lower() == "bus"


def is_company_car(vehicle_type: str) -> bool:
    return vehicle_type.lower() == "bedrijfsauto"
