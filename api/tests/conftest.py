import pytest
from django.contrib.auth.models import User
from api.models import Size, Tier, Profile

@pytest.fixture
def create_basic_user():
    payload = {
        "username": "testuser",
        "email": "user@test.pl",
        "password": "userpassword"
    }
    user = User.objects.create(**payload)

    size = Size.objects.create(width=200, height=200, thumbnail_size=True)
    tier = Tier.objects.create(name='Basic')
    tier.thumbnail_sizes.set(Size.objects.all())
    profile = Profile.objects.create(user=user, tier=tier)

    return user

@pytest.fixture
def create_premium_user():
    payload = {
        "username": "testuser2",
        "email": "user2@test.pl",
        "password": "userpassword"
    }
    user = User.objects.create(**payload)

    Size.objects.create(width=200, height=200, thumbnail_size=True)
    Size.objects.create(width=400, height=400, thumbnail_size=True)

    tier = Tier.objects.create(name='Premium', has_original_link=True)
    tier.thumbnail_sizes.set(Size.objects.filter(thumbnail_size=True))
    profile = Profile.objects.create(user=user, tier=tier)

    return user
