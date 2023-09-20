from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import PictureView

app_name = 'api'

urlpatterns = [
    path('upload', PictureView.as_view(), name='upload'),
]