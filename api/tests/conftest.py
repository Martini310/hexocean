import pytest
from django.contrib.auth.models import User
from api.models import Size, Tier, Profile, Image
from PIL import Image as PILImage
from io import BytesIO
from django.core.files.uploadedfile import SimpleUploadedFile


@pytest.fixture
def create_basic_user():
    payload = {
        "username": "basic_user",
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
        "username": "premium_user",
        "email": "user2@test.pl",
        "password": "userpassword"
    }
    user = User.objects.create(**payload)

    premium = Tier.objects.filter(name='Premium').get()
    profile = Profile.objects.create(user=user, tier=premium)

    return user

@pytest.fixture
def create_enterprise_user():
    payload = {
        "username": "enterprise_user",
        "email": "user3@test.pl",
        "password": "userpassword"
    }
    user = User.objects.create(**payload)

    enterprise = Tier.objects.filter(name='Enterprise').get()
    profile = Profile.objects.create(user=user, tier=enterprise)

    return user

@pytest.fixture
def create_image(create_enterprise_user):

    image_data = BytesIO()
    image = PILImage.new('RGB', (200, 200), 'black')
    image.save(image_data, format='png')
    image_data.seek(0)

    size = Size.objects.first()
    user = create_enterprise_user

    image = Image.objects.create(title='Test image',
                                 image=SimpleUploadedFile("test.png", image_data.read(), content_type='image/png'),
                                 size=size,
                                 user=user)

    return image
