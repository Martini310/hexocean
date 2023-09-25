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

    basic = Tier.objects.filter(name='Basic').get()
    profile = Profile.objects.create(user=user, tier=basic)

    return user

@pytest.fixture
def create_premium_user():
    payload = {
        "username": "testuser2",
        "email": "user2@test.pl",
        "password": "userpassword"
    }
    user = User.objects.create(**payload)

    premium = Tier.objects.filter(name='Premium').get()
    profile = Profile.objects.create(user=user, tier=premium)

    return user
