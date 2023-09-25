import pytest
import json
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth.models import User
from api.models import Size, Image
from PIL import Image as PILImage
from io import BytesIO

client = APIClient()

def test_pytest_working():
    assert True == True

@pytest.mark.django_db
def test_create_image_basic_user(create_basic_user):
    user = User.objects.first()
    
    image_data = BytesIO()
    image = PILImage.new('RGB', (1000, 1000), 'white')
    image.save(image_data, format='png')
    image_data.seek(0)
        
    client.force_login(user)
    url = '/api/images/'

    payload = {
        'title': 'Test image',
        'image': SimpleUploadedFile("test.png", image_data.read(), content_type='image/png')
    }
    response = client.post(url, payload, format='multipart')
    print(response.content)
    content = json.loads(response.content)
    assert response.status_code == status.HTTP_201_CREATED
    assert Size.objects.count() == 2 # Original and thumbnail
    assert Image.objects.count() == 2 # Original and thumbnail
    assert content['title'] == "Test image"
    assert ('/images/thumbnail_200x200_test' in content['image_200x200']) == True
    assert content.get('image', None) == None


@pytest.mark.django_db
def test_create_image_premium_user(create_premium_user):
    user = User.objects.get(username='testuser2')
    
    image_data = BytesIO()
    image = PILImage.new('RGB', (1000, 1000), 'black')
    image.save(image_data, format='png')
    image_data.seek(0)
        
    client.force_login(user)
    url = '/api/images/'

    payload = {
        'title': 'Test image',
        'image': SimpleUploadedFile("test.png", image_data.read(), content_type='image/png')
    }
    response = client.post(url, payload, format='multipart')
    print(response.content)
    content = json.loads(response.content)
    assert response.status_code == status.HTTP_201_CREATED
    assert Size.objects.count() == 3 # Original and thumbnail
    assert Image.objects.count() == 3 # Original and thumbnail
    assert content['title'] == "Test image"
    assert ('/images/thumbnail_200x200_test' in content['image_200x200']) == True
    assert ('/images/thumbnail_400x400_test' in content['image_400x400']) == True
    assert content.get('image', None) != None
