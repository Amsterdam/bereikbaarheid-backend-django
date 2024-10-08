from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import GEOSGeometry, Point
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models

from bereikbaarheid.models import TimeStampMixin

DEFAULT_GEOM = "SRID=28992;POINT (122025.8 488234.44)"  # water Centraal Station


class Bericht(TimeStampMixin):
    """
    Touringcar: berichten van verkeershinder en omleidingen
    """

    class Meta:
        verbose_name = "Bericht"
        verbose_name_plural = "Berichten"

    id = models.BigAutoField(primary_key=True, help_text="Id")
    title = models.CharField(max_length=255, help_text="titel")
    body = models.TextField(blank=True, null=True, help_text="onderwerp")
    advice = models.TextField(blank=True, null=True, help_text="advies")
    title_en = models.CharField(
        max_length=255, blank=True, null=True, help_text="engels: titel"
    )
    body_en = models.TextField(blank=True, null=True, help_text="engels: onderwerp")
    advice_en = models.TextField(blank=True, null=True, help_text="engels: advies")
    title_fr = models.CharField(
        max_length=255, blank=True, null=True, help_text="frans: titel"
    )
    body_fr = models.TextField(blank=True, null=True, help_text="frans: onderwerp")
    advice_fr = models.TextField(blank=True, null=True, help_text="frans: advies")
    title_de = models.CharField(
        max_length=255, blank=True, null=True, help_text="duits: titel"
    )
    body_de = models.TextField(blank=True, null=True, help_text="duits: onderwerp")
    advice_de = models.TextField(blank=True, null=True, help_text="duits: advies")
    title_es = models.CharField(
        max_length=255, blank=True, null=True, help_text="spaans: titel"
    )
    body_es = models.TextField(blank=True, null=True, help_text="spaans: onderwerp")
    advice_es = models.TextField(blank=True, null=True, help_text="spaans: advies")
    startdate = models.DateField(help_text="Publicatie startdatum")
    enddate = models.DateField(help_text="Publicatie einddatum")
    category = models.CharField(max_length=55, blank=True, null=True)
    link = models.URLField(max_length=200, blank=True, null=True)
    image_url = models.ImageField(upload_to="touringcar-images", blank=True, null=True)
    important = models.BooleanField(
        help_text="Belangrijk bericht (Komt bovenaan de lijst te staan)"
    )
    is_live = models.BooleanField(default=True, help_text="Publiceren op Tour Buzz")
    lat = models.FloatField(help_text="Latitude", blank=True, null=True)
    lon = models.FloatField(help_text="Longitude", blank=True, null=True)
    geometry = PointField(srid=28992, default=DEFAULT_GEOM)

    def clean(self):
        if (self.enddate and self.startdate) and (self.enddate < self.startdate):
            raise ValidationError({"enddate": ("enddate can not be before startdate.")})

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.lat and self.lon:  # lat, lon exist
            if self.geometry.equals_exact(
                GEOSGeometry(DEFAULT_GEOM), tolerance=0.005
            ):  # because of decimals == comparing not true
                self.geometry = calc_geometry_from_wgs(self.lat, self.lon)
            else:  # self.geometry != DEFAULT_GEOM
                pnt = calc_lat_lon_from_geometry(self.geometry)
                self.lat = pnt["lat"]
                self.lon = pnt["lon"]

        return super().save(*args, **kwargs)


def calc_geometry_from_wgs(lat: float, lon: float) -> PointField:
    """Calculate geometry in srid=28992 (RD-coordinates) from given latitude and longitude (srid=4326; WGS coordinates)"""
    point_wgs84 = Point(lon, lat, srid=4326)
    point_rd = point_wgs84.transform(28992, clone=True)
    return point_rd


def calc_lat_lon_from_geometry(geom: PointField) -> dict:
    """Calculate Point latitude and longitude (srid=4326; WGS coordinates) from given geometry in srid=28992 (RD-coordinates)"""
    point_rd = Point(geom.x, geom.y, srid=28992)
    point_wgs84 = point_rd.transform(4326, clone=True)
    return {"lat": point_wgs84.y, "lon": point_wgs84.x}


class TouringcarBase(TimeStampMixin):
    """Base model for data halte, parkeerplaatsen en doorrijhoogte"""

    class Meta:
        abstract = True

    name = models.CharField(max_length=50, help_text="omschrijving")
    lat = models.FloatField(help_text="Latitude", blank=True, null=True)
    lon = models.FloatField(help_text="Longitude", blank=True, null=True)
    geometry = PointField(srid=28992, default=DEFAULT_GEOM)

    def save(self, *args, **kwargs):
        self.full_clean()

        if self.lat and self.lon:  # lat, lon exist
            if self.geometry.equals_exact(
                GEOSGeometry(DEFAULT_GEOM), tolerance=0.005
            ):  # because of decimals == comparing not true
                self.geometry = calc_geometry_from_wgs(self.lat, self.lon)
            else:  # self.geometry != DEFAULT_GEOM
                pnt = calc_lat_lon_from_geometry(self.geometry)
                self.lat = pnt["lat"]
                self.lon = pnt["lon"]

            # Round the coordinates to 6 decimal places
            self.lat = round(self.lat, 6)
            self.lon = round(self.lon, 6)

        return super().save(*args, **kwargs)


class Halte(TouringcarBase):
    """Touringcar: haltes"""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                ],
                name="halte_name_unique",
            ),
        ]

    code = models.IntegerField(blank=True)
    location = models.CharField(max_length=150, help_text="bijzonderheden")
    capacity = models.IntegerField(help_text="plaatsen")

    def clean(self):
        check_code = self.name.split(":")[0]
        if check_code[0:1] != "H" or not check_code[1:].isnumeric():
            raise ValidationError(
                {
                    "name": (
                        "name moet beginnen met een 'H' gevolgd door een <nummer> en ':' "
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        # set numeric code from given name
        self.code = int(self.name.split(":")[0][1:])

        return super().save(*args, **kwargs)


class Parkeerplaats(TouringcarBase):
    """Touringcar: parkeerplaats (P+R)"""

    class Meta:
        verbose_name_plural = "Parkeerplaatsen"
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                ],
                name="parkeerplaats_name_unique",
            ),
        ]

    code = models.IntegerField(blank=True)
    location = models.CharField(max_length=200, help_text="bijzonderheden")
    capacity = models.IntegerField(help_text="plaatsen")
    info = models.CharField(
        max_length=100, help_text="meerInformatie", blank=True, null=True
    )
    url = models.URLField(blank=True, null=True)

    def clean(self):
        check_code = self.name.split(":")[0]
        if check_code[0:1] != "P" or not check_code[1:].isnumeric():
            raise ValidationError(
                {
                    "name": (
                        "name moet beginnen met een 'P' gevolgd door een <nummer> en ':' "
                    )
                }
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        # set numeric code from given name
        self.code = int(self.name.split(":")[0][1:])

        return super().save(*args, **kwargs)


class Doorrijhoogte(TouringcarBase):
    """Touringcar: borden Doorrijhoogte"""

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["name", "lat", "lon"], name="doorrijhoogte_name_lat_lon_unique"
            ),
        ]

    maxheight = models.CharField(
        max_length=5,
        help_text="maximaleDoorrijhoogte",
        validators=[
            RegexValidator(
                regex=r"^\d+[,]{0,1}\d{0,}m$",
                message="format voor maximaledoorijhoogte is: <cijfer>,<cijfer> gevolgd door 'm'",
            )
        ],
    )
