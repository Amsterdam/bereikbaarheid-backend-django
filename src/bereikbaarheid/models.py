from django.contrib.gis.db.models import MultiLineStringField, PointField, PolygonField
from django.contrib.postgres.fields import ArrayField
from django.db import models

"""
Docs:
https://git.data.amsterdam.nl/re_verkeer/bereikbaarheid/-/issues/459
help_text is the original table name
"""


class Gebied(models.Model):
    """
    naam oude db-tabel: bereikbaarheid.bd_gebieden
    """

    class Meta:
        verbose_name = "Gebied"
        verbose_name_plural = "Gebieden"

    geom = PolygonField(srid=28992)


class Stremming(models.Model):
    """
    naam oude db-tabel: bereikbaarheid.bd_stremming
    help_text = kolomnaam oude db-tabel
    """

    class Meta:
        verbose_name = "Stremming"
        verbose_name_plural = "Stremmingen"

    link_nr = models.IntegerField(db_index=True, help_text="vma_linknr")
    werkzaamheden = models.CharField(max_length=255)
    opmerking = models.CharField(max_length=1000, blank=True, null=True)
    kenmerk = models.CharField(max_length=255, blank=True, null=True)
    url = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()


class VenstertijdWeg(models.Model):
    """
    naam oude db-tabel: bereikbaarheid.bd_venstertijdwegen
    help_text = kolomnaam oude db-tabel
    """

    class Meta:
        verbose_name = "Venstertijdweg"
        verbose_name_plural = "Venstertijdwegen"

    link_nr = models.IntegerField(help_text="linknr")
    name = models.CharField(max_length=255, blank=True, null=True)
    e_type = models.CharField(max_length=255, blank=True, null=True)
    verkeersbord = models.CharField(max_length=255, blank=True, null=True)
    dagen = ArrayField(models.CharField(max_length=10, blank=True, null=True))
    begin_tijd = models.TimeField(blank=True, null=True)
    eind_tijd = models.TimeField(blank=True, null=True)


class VerkeersBord(models.Model):
    """
    naam oude db-tabel: bereikbaarheid.bd_verkeersborden
    help_text = kolomnaam oude db-tabel
    """

    class Meta:
        verbose_name = "Verkeersbord"
        verbose_name_plural = "Verkeersborden"

    bord_id = models.IntegerField(unique=True)
    geldigheid = models.CharField(max_length=99)
    rvv_modelnummer = models.CharField(max_length=25)
    tekst = models.CharField(max_length=25, blank=True, null=True)
    kijkrichting = models.IntegerField()
    link_nr = models.IntegerField(help_text="script_link_nr")
    link_gevalideerd = models.IntegerField()
    tekst_waarde = models.FloatField(blank=True, null=True)
    onderbord_tekst = models.CharField(max_length=299, blank=True, null=True)
    verkeersbesluit = models.CharField(max_length=50, blank=True, null=True)
    versie = models.DateField()
    rd_x = models.IntegerField()
    rd_y = models.IntegerField()
    link_validated_2 = models.IntegerField()
    panorama = models.CharField(max_length=500, blank=True, null=True)
    geometry = PointField(srid=28992, blank=True)

    def save(self, *args, **kwargs):
        self.geometry = f"POINT({self.rd_x} {self.rd_y})"
        return super().save(*args, **kwargs)


class VerkeersTelling(models.Model):
    """
    naam oude db-tabel: bereikbaarheid.bd_verkeerstellingen
    help_text = kolomnaam oude db-tabel
    """

    class Meta:
        verbose_name = "Verkeerstelling"
        verbose_name_plural = "Verkeerstellingen"

    volg_nummer = models.IntegerField(help_text="Volgnummer")
    lat = models.FloatField(help_text="Latitude")
    lon = models.FloatField(help_text="Longitude")
    link_nr = models.IntegerField(blank=True, null=True, help_text="vma_link_nr")
    url = models.CharField(max_length=255)
    telpunt_naam = models.CharField(max_length=255, help_text="Telpuntnaam")
    tussen = models.CharField(max_length=255, help_text="Tussen")
    richtingen_1 = models.CharField(max_length=255, help_text="Richtingen_1")
    richtingen_2 = models.CharField(max_length=255, help_text="Richtingen_2")
    jaar = models.IntegerField()
    storing = models.CharField(max_length=255, help_text="storing")
    type_verkeer = models.CharField(max_length=255, help_text="Type_verkeer")
    langzaam_verkeer = models.BooleanField(help_text="Langzaam_verkeer")
    snel_verkeer = models.BooleanField(help_text="Snel_verkeer")
    bijzonderheden = models.CharField(max_length=255, help_text="Bijzonderheden")
    meet_methode = models.CharField(max_length=255, help_text="Meetmethode")


class Verrijking(models.Model):
    """
    naam oude db-tabel: bereikbaarheid.bd_vma_beleidsmatige_verrijking
    help_text = kolomnaam oude db-tabel
    """

    class Meta:
        verbose_name = "Verrijking"
        verbose_name_plural = "Verrijkingen"

    link_nr = models.IntegerField(help_text="linknr")
    binnen_amsterdam = models.BooleanField(blank=True, null=True)
    binnen_polygoon_awb = models.BooleanField(blank=True, null=True)
    milieuzone = models.BooleanField(
        blank=True,
        null=True,
    )
    zone_zwaar_verkeer_bus = models.BooleanField(blank=True, null=True)
    zone_zwaar_verkeer_non_bus = models.BooleanField(blank=True, null=True)
    zone_zwaar_verkeer_detail = models.CharField(
        blank=True,
        null=True,
        max_length=255,
    )
    tunnelcategorie_gevaarlijke_stoffen = models.CharField(
        max_length=29, blank=True, null=True
    )
    tunnelnamen = models.CharField(max_length=29, blank=True, null=True)
    route_gevaarlijke_stoffen = models.CharField(max_length=29, blank=True, null=True)
    beleidsnet_auto = models.CharField(max_length=29, blank=True, null=True)
    beleidsnet_ov = models.CharField(max_length=29, blank=True, null=True)
    beleidsnet_fiets = models.CharField(max_length=29, blank=True, null=True)
    beleidsnet_lopen = models.CharField(max_length=29, blank=True, null=True)
    hoofdroute_taxi = models.CharField(max_length=29, blank=True, null=True)
    touringcar_aanbevolen_routes = models.CharField(
        max_length=29, blank=True, null=True
    )
    wettelijke_snelheid_actueel = models.IntegerField(blank=True, null=True)
    wettelijke_snelheid_wens = models.IntegerField(blank=True, null=True)
    wegcategorie_actueel = models.CharField(blank=True, null=True, max_length=29)
    wegcategorie_wens = models.CharField(blank=True, null=True, max_length=29)
    frc = models.IntegerField(blank=True, null=True)


class Lastbeperking(models.Model):
    """
    naam oude db-tabel: bereikbaarheid.lastbeperking_in_zzv_zonder_vb
    """

    class Meta:
        verbose_name = "Lastbeperking"
        verbose_name_plural = "Lastbeperkingen"

    link_nr = models.IntegerField()
    lastbeperking_in_kg = models.FloatField(blank=True, null=True)


class Vma(models.Model):
    """
    naam oude db-tabel: bereikbaarheid.bd_vma_latest
    help_text = kolomnaam oude db-tabel
    """

    class Meta:
        verbose_name = "Vma"
        verbose_name_plural = "Vma"

    link_nr = models.FloatField()  # blank=True, null=True)
    name = models.CharField(max_length=50, blank=True, null=True)
    direction = models.FloatField(blank=True, null=True)
    length = models.FloatField(blank=True, null=True)
    anode = models.FloatField(blank=True, null=True)
    bnode = models.FloatField(blank=True, null=True)
    wegtypeab = models.CharField(max_length=50, blank=True, null=True)
    wegtypeba = models.CharField(max_length=50, blank=True, null=True)
    speedab = models.FloatField(blank=True, null=True)
    speedba = models.FloatField(blank=True, null=True)
    wegtype_ab = models.CharField(max_length=50, blank=True, null=True)
    wegtype_ba = models.CharField(max_length=50, blank=True, null=True)
    geom = MultiLineStringField(srid=28992)


class VerkeersPaal(models.Model):
    """
    naam oude db-tabel: bereikbaarheid.bd_verkeerspalen
    help_text = kolomnaam oude db-tabel
    """

    class Meta:
        verbose_name = "Verkeerspaal"
        verbose_name_plural = "Verkeerspalen"

    link_nr = models.IntegerField(help_text="linknr")
    paal_nr = models.CharField(
        max_length=255, blank=True, null=True, help_text="paalnummer"
    )
    verkeersbord = models.CharField(max_length=255, blank=True, null=True)
    dagen = ArrayField(models.CharField(max_length=10))
    begin_tijd = models.TimeField()
    eind_tijd = models.TimeField()
    geometry = PointField(srid=28992)
    type = models.CharField(max_length=255, blank=True, null=True)
    standplaats = models.CharField(max_length=255, blank=True, null=True)
    jaar_aanleg = models.IntegerField(blank=True, null=True)
    venstertijden = models.CharField(max_length=255, blank=True, null=True)
    toegangssysteem = models.CharField(max_length=255, blank=True, null=True)
    camera = models.CharField(max_length=255, blank=True, null=True)
    beheerorganisatie = models.CharField(max_length=255, blank=True, null=True)
    bijzonderheden = models.CharField(max_length=500, blank=True, null=True)
