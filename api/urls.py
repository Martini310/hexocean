from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from .views import ImageViewSet, TierViewSet, SizeViewSet
from rest_framework.routers import DefaultRouter


app_name = 'api'

router = DefaultRouter()

# router.register('pictures', PictureViewSet, basename='pictures')
router.register('images', ImageViewSet, basename='images')
router.register('Tier', TierViewSet, basename='Tier')
router.register('Size', SizeViewSet, basename='Size')

urlpatterns = [
    path('', include(router.urls)),
    # path('upload/', PictureViewSet.as_view({'get': 'list', 'post': 'create'}), name='upload'),
]
