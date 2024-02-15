import pytest
from django.contrib.auth.models import Group, User
from model_bakery import baker

from main.auth import OIDCAuthenticationBackend


@pytest.fixture
def django_group_bereikbaarheid():
    return baker.make(Group, name= 'bereikbaarheid')

@pytest.fixture
def django_group_touringcar():
    return baker.make(Group, name= 'touringcar')

class Test_auth:

    @pytest.mark.parametrize(
        "key, test_claims, expected",
        [
            (1,  {'name': 'test', 'family_name': 'family_test', 'given_name': 'Test', 'email': 'test@amsterdam.nl', 'roles': ['o-bereikbaarheid-application-admin']},
                "<QuerySet []>",
             ),
            (2, {'name': 'test', 'family_name': 'family_test', 'given_name': 'Test', 'email': 'test@amsterdam.nl', 'roles': ['o-bereikbaarheid-app-admin-bereikbaarheid']},
                "<QuerySet ['bereikbaarheid']>",
             ),
            (3,  {'name': 'test', 'family_name': 'family_test', 'given_name': 'Test', 'email': 'test@amsterdam.nl', 'roles': ['o-bereikbaarheid-app-admin-touringcar']},
                "<QuerySet ['touringcar']>",
             ),
            (4, {'name': 'test', 'family_name': 'family_test', 'given_name': 'Test', 'email': 'test@amsterdam.nl', 'roles': ['o-bereikbaarheid-app-admin-bereikbaarheid','o-bereikbaarheid-app-admin-touringcar']},
                "<QuerySet ['bereikbaarheid', 'touringcar']>",
             ),
        ],
    )
    @pytest.mark.django_db
    def test_update_group(self, django_group_bereikbaarheid, django_group_touringcar, key, test_claims, expected):
        OIDC = OIDCAuthenticationBackend()
        OIDC.create_user(test_claims)

        user = User.objects.get(pk=key)
        assert user.last_name == "family_test"
        assert str(user.groups.values_list('name',flat = True)) == expected