import datetime

import pandas as pd
import pytest
from django.core.exceptions import ValidationError
from model_bakery import baker

from bereikbaarheid.models import Gebied, VerkeersPaal, Verrijking, Vma
from bereikbaarheid.resources.utils import (
    GEOJSON,
    SCSV,
    clean_dataset_headers,
    convert_str,
    convert_to_date,
    convert_to_time,
    refresh_materialized,
    remove_chars_from_value,
    truncate,
)
from bereikbaarheid.utils import django_query_db


@pytest.fixture
def bollard():
    """Fixture for baked Verkeerspaal model"""
    return baker.make(VerkeersPaal)


@pytest.fixture
def vma():
    """Fixture for baked Verkeerspaal model"""
    return baker.make(
        Vma,
        link_nr=473943,
        wegtypeab="etw bibeko 1",
        wegtypeba="etw bibeko 1",
        geom="SRID=28992;MULTILINESTRING ((120153.413895163 483319.6382638101, 120146.435625 483344.40625))",
    )  # gustav mahlerplein


@pytest.fixture
def gebied():
    """Fixture for baked Verkeerspaal model"""
    return baker.make(
        Gebied,
        geom="SRID=28992;POLYGON ((120203.682 483505.082, 120106.283 483505.621, 119984.852 483503.38300000003, 119887.444 483497.496, 119661.087 483480.204, 119668.431 483133.245, 120218.756 483130.863, 120301.15 483133.45, 120337.891 483139.189, 120234.275 483351.77, 120228.294 483366.342, 120222.942 483381.157, 120214.162 483411.406, 120207.999 483442.294, 120204.497 483473.59500000003, 120203.682 483505.082))",
    )


@pytest.fixture
def verrijking():
    """Fixture for baked Verkeerspaal model"""
    return baker.make(Verrijking, link_nr=473943)


testgeojson = {
    "type": "FeatureCollection",
    "name": "sql_statement",
    "crs": {"type": "name", "properties": {"name": "urn:ogc:def:crs:EPSG::28992"}},
    "features": [
        {
            "type": "Feature",
            "properties": {"code": "A01f"},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [121181.182, 487312.011],
                        [121179.256, 487345.803000000014435],
                        [121180.518, 487371.117000000027474],
                        [121062.5, 487381.508000000030734],
                        [121060.131, 487368.90400000003865],
                        [121056.237, 487356.819000000017695],
                        [121038.176, 487277.51500000001397],
                        [121010.554, 487052.617000000027474],
                        [120989.112, 486886.109],
                        [120989.888, 486881.76300000003539],
                        [120990.653, 486877.48499999998603],
                        [121004.68, 486852.117000000027474],
                        [121037.134, 486810.831],
                        [121069.967, 486853.661000000021886],
                        [121075.887, 486862.930999999982305],
                        [121081.77, 486874.334000000031665],
                        [121086.227, 486885.482000000018161],
                        [121089.633, 486896.995],
                        [121093.389, 486946.163999999989755],
                        [121104.353, 486986.232000000018161],
                        [121118.176, 487028.769000000029337],
                        [121142.589, 487079.461000000010245],
                        [121152.07, 487094.709000000031665],
                        [121160.312, 487111.270000000018626],
                        [121179.5, 487164.407],
                        [121182.856, 487176.13900000002468],
                        [121184.848, 487188.178000000014435],
                        [121185.447, 487200.87400000001071],
                        [121183.677, 487268.332],
                        [121181.182, 487312.011],
                    ]
                ],
            },
        },
    ],
}


@pytest.fixture
def csv_file():
    d = {15279: None, 19338: 7500.0}
    df = pd.DataFrame(d.items(), columns=["linknr", "lastbeperking_in_kg"])
    return df.to_csv(index=False)


@pytest.fixture
def csv_file_semicolon():
    d = {15279: None, 19338: 7500.0}
    df = pd.DataFrame(d.items(), columns=["linknr", "lastbeperking_in_kg"])
    return df.to_csv(index=False, sep=";")


class TestUtils:
    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("16/03/22 0:00", datetime.datetime(2022, 3, 16, 0, 0)),
            ("2022-02-11 00:00:00.000", datetime.datetime(2022, 2, 11, 0, 0)),
        ],
    )
    def test_convert_to_date_pass(self, test_input, expected):
        """Value with format %d/%m/%y %H:%M of %Y-%m-%d %H:%M:%S.%f, can be converted to datetime format"""
        assert convert_to_date(test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected", [("22-03-17", "verkeerd"), ("test", "verkeerd")]
    )
    def test_convert_to_date_exception(self, test_input, expected):
        """Raise an exception if value can't be converted to datetime format"""
        with pytest.raises(ValueError) as e:
            convert_to_date(test_input)
        assert str(e.value)[0:8] == expected

    @pytest.mark.parametrize(
        "test_input, expected",
        [
            ("12:00", datetime.time(12, 0)),
            ("13:00:59", datetime.time(13, 0, 59)),
            ("1", datetime.time(1, 0)),
        ],
    )
    def test_convert_to_time_pass(self, test_input, expected):
        """Raise an exception if string can't be converted to needed time format"""
        assert convert_to_time(test_input) == expected

    @pytest.mark.parametrize(
        "test_input, expected", [("test", "verkeerd"), ("10.05", "verkeerd")]
    )
    def test_convert_to_time_exception(self, test_input, expected):
        """Raise an exception if string can't be converted to needed time format"""
        with pytest.raises(ValueError) as e:
            convert_to_time(test_input)
        assert str(e.value)[0:8] == expected

    @pytest.mark.parametrize(
        "test_input, test_to, expected",
        [
            ("1200", "float", 1200),
            ("1", "float", float(1)),
            ("test", "float", "test"),
            ("4", "set", "4"),
        ],
    )
    def test_convert_str(self, test_input, test_to, expected):
        """Return to:format(value) else return value"""

        assert convert_str(test_input, test_to) == expected

    @pytest.mark.parametrize(
        "test_input, charlist, expected",
        [
            ("test!help", "!5", "testhelp"),
            ("test!help", "t!hl", "esep"),
        ],
    )
    def test_remove_chars_from_value(self, test_input, charlist, expected):
        """Return: test_input without charlist-characters"""
        assert remove_chars_from_value(test_input, charlist) == expected

    @pytest.mark.parametrize(
        "test_headers, test_col_mapping, expected",
        [
            (
                ["linknr", "banaan"],
                {"linknr": "link_nr", "banaan": "appel"},
                ["link_nr", "appel"],
            ),
            (
                ["link", "BanaaN"],
                {"linknr": "link_nr", "banaan": "appel"},
                ["link", "appel"],
            ),
        ],
    )
    def test_clean_dataset_headers(self, test_headers, test_col_mapping, expected):
        """apply col_mapping and strip().lower() on list"""
        assert clean_dataset_headers(test_headers, test_col_mapping) == expected

    @pytest.mark.django_db
    def test_truncate(self, bollard):
        """truncate db table and restart AutoField primary_key for import"""
        # verkeerspaal = VerkeersPaal.objects.create(bollard)
        bollard.save()
        assert VerkeersPaal.objects.all().count() == 1
        assert VerkeersPaal.objects.get(pk=1) == bollard

        truncate(VerkeersPaal)

        assert VerkeersPaal.objects.all().count() == 0
        # test id reset
        bollard.save()
        assert VerkeersPaal.objects.get(pk=1) == bollard

    def test_GEJSON(self):
        gj = GEOJSON()
        ds = gj.create_dataset(testgeojson)
        assert ds.headers == ["code", "geom"]

    def test_SCSV_raise(self, csv_file):
        sc = SCSV()
        with pytest.raises(ValidationError) as e:
            sc.create_dataset(csv_file)
        assert (
            str(e.value)
            == "['file is using `,` delimiter, but semicolon_csv format is with `;` delimiter']"
        )

    def test_SCSV(self, csv_file_semicolon):
        sc = SCSV()
        ds = sc.create_dataset(csv_file_semicolon)
        assert ds.headers == ["linknr", "lastbeperking_in_kg"]

    @pytest.mark.django_db
    def test_refresh_materialized(self, vma, gebied, verrijking):
        vma.save()
        gebied.save()
        verrijking.save()
        refresh_materialized("bereikbaarheid_out_vma_undirected")

        raw_query = f"""
            SELECT count(*) FROM bereikbaarheid_out_vma_undirected GROUP BY name
            """
        result = django_query_db(raw_query, {})
        assert len(result) == 1
