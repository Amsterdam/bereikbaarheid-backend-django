from django.contrib.gis.db.models import PointField
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.db import models

from bereikbaarheid.models import TimeStampMixin

DEFAULT_GEOM = "SRID=28992;POINT (122025.8 488234.44)" #water Centraal Station


class Bericht(TimeStampMixin):
    """
    Touringcar: berichten van verkeershinder en omleidingen
    """

    class Meta:
        verbose_name = "Bericht"
        verbose_name_plural = "Berichten"

    id = models.BigAutoField(primary_key=True, help_text="Id")
    title = models.CharField(max_length=255, help_text="titel")
    body =  models.TextField(blank=True, null=True, help_text="onderwerp")
    advice =  models.TextField(blank=True, null=True, help_text="advies")
    title_en =  models.CharField(max_length=255, blank=True, null=True, help_text="engels: titel")
    body_en =  models.TextField(blank=True, null=True, help_text="engels: onderwerp")
    advice_en =  models.TextField(blank=True, null=True, help_text="engels: advies")
    title_fr =  models.CharField(max_length=255, blank=True, null=True, help_text="frans: titel")
    body_fr =   models.TextField(blank=True, null=True, help_text="frans: onderwerp")
    advice_fr =   models.TextField(blank=True, null=True, help_text="frans: advies")
    title_de =  models.CharField(max_length=255, blank=True, null=True, help_text="duits: titel")
    body_de =   models.TextField(blank=True, null=True, help_text="duits: onderwerp")
    advice_de =   models.TextField(blank=True, null=True, help_text="duits: advies")
    title_es =  models.CharField(max_length=255, blank=True, null=True, help_text="spaans: titel")
    body_es =   models.TextField(blank=True, null=True, help_text="spaans: onderwerp")
    advice_es =   models.TextField(blank=True, null=True, help_text="spaans: advies")
    startdate = models.DateField(help_text="Publicatie startdatum")
    enddate = models.DateField(help_text="Publicatie einddatum")
    category = models.CharField(max_length=55, blank=True, null=True)
    link = models.URLField(max_length = 200, blank=True, null=True)
    image_url = models.ImageField(upload_to='images', blank=True, null=True)
    important = models.BooleanField(help_text="Belangrijk bericht (Komt bovenaan de lijst te staan)")
    is_live = models.BooleanField(default=True, help_text= "Publiceren op Tour Buzz")
    lat = models.FloatField(help_text="Latitude", blank=True, null=True)
    lon = models.FloatField(help_text="Longitude",  blank=True, null=True)
    geometry = PointField(srid=28992, default=DEFAULT_GEOM)

    def clean(self):
        if (self.enddate and self.startdate) and (self.enddate < self.startdate):
            raise ValidationError(
                {"enddate": ("enddate can not be before startdate.")}
            )

    def save(self, *args, **kwargs):  
        self.full_clean()

        if (self.lat and self.lon): #lat, lon exist
            if self.geometry != DEFAULT_GEOM: 
                pnt = calc_lat_lon_from_geometry(self.geometry)
                self.lat = pnt['lat']
                self.lon = pnt['lon']
            else: 
                self.geometry = calc_geometry_from_wgs(self.lat, self.lon)                

        return super().save(*args, **kwargs) 


def calc_geometry_from_wgs(lat:float, lon:float) -> PointField:
    '''Calculate geometry in srid=28992 (RD-coordinates) from given latitude and longitude (srid=4326; WGS coordinates)'''
    pnt = Point(lon, lat, srid=4326)
    pnt.transform(28992)
    return pnt

def calc_lat_lon_from_geometry(geom: PointField) -> dict:
    '''Calculate Point latitude and longitude (srid=4326; WGS coordinates) from given geometry in srid=28992 (RD-coordinates)'''
    pnt = Point(geom.x, geom.y, srid=28992)
    pnt.transform(4326)
    return {'lat': pnt.y, 'lon': pnt.x}
