import pytest
from django.core.exceptions import ValidationError
from model_bakery import baker

from bereikbaarheid.models import VenstertijdWeg


class TestModelValidation:
    """test custom validators set on modelfields"""

    @pytest.mark.parametrize(
        "testname",
        [("1e Jacob van Campenstr"), ("Telpunt: Verlengde Stellingweg (S118)")],
    )
    @pytest.mark.django_db
    def test_modelfield_name_goed(self, testname):
        test = baker.prepare(VenstertijdWeg, name=testname, dagen=["ma", "di"])
        test.full_clean()

    @pytest.mark.parametrize(
        "testname",
        [
            ("$"),
            ("=cmd|"),
            ("select name from table;"),
        ],
    )
    @pytest.mark.django_db
    def test_modelfield_name_error(self, testname):
        with pytest.raises(ValidationError) as excinfo:
            test = baker.prepare(VenstertijdWeg, name=testname, dagen=["ma", "di"])
            test.full_clean()

        assert "Specialcharacters" in str(excinfo.value)
