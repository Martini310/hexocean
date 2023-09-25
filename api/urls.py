from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from .views import ImageView, download_image, generate_link #, TierViewSet, SizeViewSet


app_name = 'api'

router = DefaultRouter()

# Unused for now, create and edit only in Admin Panel
# router.register('Tier', TierViewSet, basename='Tier')
# router.register('Size', SizeViewSet, basename='Size')

urlpatterns = [
    # path('', include(router.urls)),
    path('download/<slug:slug>/', download_image, name='download_image'),
    path('generate-link/', generate_link, name='generate_link'),
    path('images/', ImageView.as_view(), name='images')
]
