from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import SizeSerializer, TierSerializer, ImageSerializer
from .models import Size, Tier, Image
from PIL import Image as PILImage
from io import BytesIO
import os
from core.settings import MEDIA_URL, MEDIA_ROOT
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from .models import TemporaryLink
from django.utils import timezone
from django.core.exceptions import PermissionDenied


def download_image(request, slug):
    link = get_object_or_404(TemporaryLink, slug=slug)
    print(timezone.now(), link.exp_date)
    # Ensure that the link is still valid (check the expiration date)
    if timezone.now() > link.exp_date:
        raise PermissionDenied()
    
    # Get the image file associated with the link
    image_file = link.image.image

    # Serve the image as a downloadable file
    response = FileResponse(image_file, content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{image_file.name}"'
    
    return response

class SizeViewSet(viewsets.ModelViewSet):

    queryset = Size.objects.all()
    serializer_class = SizeSerializer
    permission_classes = [permissions.IsAuthenticated]


class TierViewSet(viewsets.ModelViewSet):

    queryset = Tier.objects.all()
    serializer_class = TierSerializer
    permission_classes = [permissions.IsAuthenticated]


class ImageViewSet(viewsets.ModelViewSet):
    
    serializer_class = ImageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Image.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Get the user's tier
        user_tier = self.request.user.profile.tier

        # Calculate thumbnail sizes based on the user's tier
        thumbnail_sizes = user_tier.thumbnail_sizes.all() if user_tier else []

        # Save the original image
        image = serializer.validated_data['image']
        image_instance = self.save_original_image(image, serializer.validated_data['title'])

        # Create and save thumbnails
        self.create_and_save_thumbnails(image, thumbnail_sizes)

        # Create a Response dictionary with links to all resolutions
        response_data = serializer.data
        # Add path to original size
        response_data['image'] = image_instance.image.url
        # Add paths to all thumbnails
        for size in thumbnail_sizes:
            response_data[f'image_{size}'] = f"{MEDIA_URL}thumbnail_{size.width}x{size.height}_{image_instance.image.name}"

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


    def create_and_save_thumbnails(self, image, thumbnail_sizes):
        for size in thumbnail_sizes:
            thumbnail = self.create_thumbnail(image, size)
            thumbnail_name = f"thumbnail_{size.width}x{size.height}_{image.name}"
            tmp_thumbnail = BytesIO()
            thumbnail.save(tmp_thumbnail, format='JPEG' if image.name.lower().endswith('.jpg') else 'PNG')
            thumbnail_instance = Image(
                title=thumbnail_name,
                user=self.request.user,
                size=size,
            )
            thumbnail_instance.image.save(thumbnail_name, tmp_thumbnail, save=False)
            thumbnail_instance.save()


    def save_original_image(self, image, title):
        image_instance = Image(
            title=title,
            user=self.request.user,
        )
        image_instance.image.save(image.name, image, save=False)
        image_instance.save()
        return image_instance

    def create_thumbnail(self, image_file, size):
        try:
            img = PILImage.open(image_file)
            img.thumbnail((size.width, size.height), PILImage.LANCZOS)
            return img
        except Exception as e:
            # Handle exceptions here, e.g., log the error or return a default image.
            print(f'-----{e}------')

