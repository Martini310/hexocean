from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import PictureViewSet

app_name = 'api'

urlpatterns = [
    path('upload/', PictureViewSet.as_view({'get': 'list', 'post': 'create'}), name='upload'),
]
