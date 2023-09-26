import pytest
import json
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from api.models import Size, Image, TemporaryLink
from PIL import Image as PILImage
from io import BytesIO
from django.urls import reverse


client = APIClient()

def test_pytest_working():
    assert True == True

@pytest.mark.django_db
def test_basic_user_create_image(create_basic_user):
    user = User.objects.get(username='basic_user')
    
    image_data = BytesIO()
    image = PILImage.new('RGB', (1000, 1000), 'white')
    image.save(image_data, format='png')
    image_data.seek(0)
        
    client.force_login(user)

    url = reverse('api:images')

    payload = {
        'title': 'Test image',
        'image': SimpleUploadedFile("test.png", image_data.read(), content_type='image/png')
    }
    response = client.post(url, payload, format='multipart')
    print(response.content)
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert Size.objects.count() == 3 # Original and 2 thumbnails (200px and 400px)
    assert Image.objects.count() == 1 # Original and thumbnail
    assert Image.objects.filter(user=user).count() == 1
    assert content['title'] == "Test image"
    assert ('/images/thumbnail_200x200_test' in content['image_200x200']) == True
    assert content.get('image_400X400', None) == None
    assert content.get('image', None) == None


@pytest.mark.django_db
def test_premium_user_create_image(create_premium_user):
    user = User.objects.get(username='premium_user')
    
    image_data = BytesIO()
    image = PILImage.new('RGB', (1000, 1000), 'black')
    image.save(image_data, format='png')
    image_data.seek(0)
        
    client.force_login(user)

    url = reverse('api:images')

    payload = {
        'title': 'Test image',
        'image': SimpleUploadedFile("test.png", image_data.read(), content_type='image/png')
    }

    response = client.post(url, payload, format='multipart')
    print(response.content)
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert Size.objects.count() == 3 # Original and 2 thumbnails (200px and 400px)
    assert Image.objects.count() == 3 # Original and 2 thumbnails (200px and 400px)
    assert content['title'] == "Test image"
    assert ('/images/thumbnail_200x200_test' in content['image_200x200']) == True
    assert ('/images/thumbnail_400x400_test' in content['image_400x400']) == True
    assert ('images/test' in content['image']) == True


@pytest.mark.django_db
def test_enterprise_user_create_image(create_enterprise_user):
    user = User.objects.get(username='enterprise_user')
    
    image_data = BytesIO()
    image = PILImage.new('RGB', (1000, 1000), 'black')
    image.save(image_data, format='png')
    image_data.seek(0)
        
    client.force_login(user)

    url = reverse('api:images')

    payload = {
        'title': 'Test image',
        'image': SimpleUploadedFile("test.png", image_data.read(), content_type='image/png')
    }

    response = client.post(url, payload, format='multipart')
    print(response.content)
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_201_CREATED
    assert Size.objects.count() == 3 # Original and 2 thumbnails (200px and 400px)
    assert Image.objects.count() == 3 # Original and 2 thumbnails (200px and 400px)
    assert content['title'] == "Test image"
    assert ('/images/thumbnail_200x200_test' in content['image_200x200']) == True
    assert ('/images/thumbnail_400x400_test' in content['image_400x400']) == True
    assert ('images/test' in content['image']) == True


@pytest.mark.django_db
def test_basic_user_cannot_generate_link(create_basic_user):
    user = User.objects.get(username='basic_user')

    client.force_login(user)
    url = reverse('api:generate_link')

    payload = {
        'image_id': 1,
        'exp_time': 300
    }

    response = client.post(url, payload)
    print(response.content)
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert content['error'] == 'This feature is not available in your plan'


@pytest.mark.django_db
def test_premium_user_cannot_generate_link(create_premium_user):
    user = User.objects.get(username='premium_user')

    client.force_login(user)
    url = reverse('api:generate_link')

    payload = {
        'image_id': 1,
        'exp_time': 300
    }

    response = client.post(url, payload)
    print(response.content)
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert content['error'] == 'This feature is not available in your plan'


@pytest.mark.django_db
def test_enterprise_user_cannot_generate_link_wrong_time(create_enterprise_user):
    user = User.objects.get(username='enterprise_user')

    client.force_login(user)
    url = reverse('api:generate_link')

    payload = {
        'image_id': 1,
        'exp_time': 200
    }

    response = client.post(url, payload)
    print(response.content)
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_200_OK
    assert content['error'] == 'expiration time should be between 300 and 30000'


@pytest.mark.django_db
def test_enterprise_user_can_generate_link(create_image):
    user = User.objects.get(username='enterprise_user')
    image = create_image
    client.force_login(user)
    url = reverse('api:generate_link')

    payload = {
        'image_id': 1,
        'exp_time': 300
    }

    response = client.post(url, payload)
    print(response.content)
    content = json.loads(response.content)
    link = TemporaryLink.objects.first()
    assert response.status_code == status.HTTP_200_OK
    assert content['url'] == link.url


@pytest.mark.django_db
def test_enterprise_user_cannot_generate_link_no_image(create_image):

    user = User.objects.get(username='enterprise_user')

    client.force_login(user)
    url = reverse('api:generate_link')

    payload = {
        'image_id': 2,
        'exp_time': 300
    }

    response = client.post(url, payload)
    print(response.content)
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert content['error'] == 'Image not found'


@pytest.mark.django_db
def test_enterprise_user_cannot_generate_link_others_image(create_image, create_second_image):
    
    second_image = create_second_image

    user = User.objects.get(username='enterprise_user')

    client.force_login(user)
    url = reverse('api:generate_link')

    payload = {
        'image_id': second_image.id,
        'exp_time': 300
    }

    response = client.post(url, payload)
    print(response.content)
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert content['error'] == 'This is not your photo'


@pytest.mark.django_db
def test_enterprise_user_cannot_create_image_wrong_format(create_enterprise_user):
    user = User.objects.get(username='enterprise_user')
    
    image_data = BytesIO()
    image = PILImage.new('RGB', (1000, 1000), 'black')
    image.save(image_data, format='gif')
    image_data.seek(0)
        
    client.force_login(user)

    url = reverse('api:images')

    payload = {
        'title': 'Test gif image',
        'image': SimpleUploadedFile("test.gif", image_data.read(), content_type='image/gif')
    }

    response = client.post(url, payload, format='multipart')
    print(response.content)
    content = json.loads(response.content)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert content['image'][0] == "Only .jpg and .png files are allowed."
