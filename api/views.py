import os
from io import BytesIO
from mimetypes import guess_type
from PIL import Image as PILImage
from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import MethodNotAllowed, PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
# from django.core.exceptions import PermissionDenied
from django.core.files.images import get_image_dimensions
from django.http import JsonResponse
from core.settings import MEDIA_URL
from .serializers import SizeSerializer, TierSerializer, ImageSerializer, ImagePostSerializer
from .models import Size, Tier, Image, TemporaryLink


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def generate_link(request):
    """
        Generate a temporary link to download an image
    """
    try:
        # Check if the user is allowed to generate expiring links
        if not request.user.profile.tier.can_generate_expiring_links:
            raise PermissionDenied('This feature is not available in your plan')

        data = request.POST

        # Check if the exp_time value is in range
        if not 300 <= int(data.get('exp_time')) <= 30000:
             return JsonResponse({'error': 'expiration time should be between 300 and 30000'})
        
        # Retrieve the image and check ownership
        image = Image.objects.get(id=data.get('image_id'))
        if image.user != request.user:
            raise PermissionDenied('This is not your photo')

        # Create a temporary link
        link = TemporaryLink.objects.create(image=image, exp_time=int(data.get('exp_time')))

        # Return the link as a JSON response
        return JsonResponse({'url': link.url, 'expiration': link.exp_date})

    except Image.DoesNotExist:
        return JsonResponse({'error': 'Image not found'}, status=404)

    except PermissionDenied as e:
        return JsonResponse({'error': str(e)}, status=403)


@api_view(['GET'])
def download_image(request, slug):
    link = get_object_or_404(TemporaryLink, slug=slug)

    # Ensure that the link is still valid (check the expiration date)
    if timezone.now() > link.exp_date:
        return JsonResponse({'error': 'Link expired'}, status=404)
    
    # Get the image file associated with the link
    image_file = link.image.image

    # Determine the content type based on the image's file extension
    content_type, _ = guess_type(image_file.name)

    # Serve the image as a downloadable file with the correct content type
    response = FileResponse(image_file, content_type=content_type)
    response['Content-Disposition'] = f'attachment; filename="{image_file.name}"'
    
    return response


class SizeViewSet(viewsets.ModelViewSet):

    queryset = Size.objects.filter(thumbnail_size=True)
    serializer_class = SizeSerializer
    permission_classes = [permissions.IsAdminUser]


class TierViewSet(viewsets.ModelViewSet):

    queryset = Tier.objects.all()
    serializer_class = TierSerializer
    permission_classes = [permissions.IsAdminUser]


class ImageViewSet(viewsets.ModelViewSet):
    
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ImagePostSerializer
        return ImageSerializer
    

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
        
        # Get the image dimensions
        width, height = get_image_dimensions(image)

        # Create and save a Size instance if not exist
        if Size.objects.filter(width=width, height=height):
            size_instance = Size.objects.get(width=width, height=height)
        else:
            size_instance = Size.objects.create(width=width, height=height)

        # Associate the Size instance with the image
        image_instance.size = size_instance
        image_instance.save()
        
        # Create and save thumbnails
        thumbnail_instances = self.create_and_save_thumbnails(image, thumbnail_sizes)

        # Create a Response dictionary with links to all resolutions
        response_data = self.create_response(user_tier, serializer.data, image_instance, thumbnail_instances, width, height)

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


    def create_response(self, user_tier, serializer_data, image_instance, thumbnail_instances, width, height):
        response_data = serializer_data

        if user_tier.has_original_link:
            # Add path to original size
            response_data['image'] = image_instance.image.url
            response_data['size'] = {'width': width, 'height': height}
        else:
            del response_data['image']
            del response_data['size']

        # Add paths to all created thumbnails
        for instance in thumbnail_instances:
            response_data[f'image_{instance.size}'] = f"{MEDIA_URL}{instance.image.name}"

        return response_data


    def create_and_save_thumbnails(self, image, thumbnail_sizes):
        thumbnail_instances = []
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
            thumbnail_instances.append(thumbnail_instance)
        return thumbnail_instances


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
            # Create thumbnail with set height and proportional width
            img.thumbnail((img.width * size.height // size.width, size.height), PILImage.LANCZOS)
            return img
        except Exception as e:
            # Handle exceptions here, e.g., log the error or return a default image.
            print(f'-----{e}------')


    def update(self, request, pk=None):
        raise MethodNotAllowed('PUT', detail='Method "PUT" not allowed')

    def partial_update(self, request, pk=None):
        raise MethodNotAllowed(method='PATCH', detail='Method "PATCH" not allowed')
    
    def destroy(self, request, pk=None):
        raise MethodNotAllowed(method='DELETE', detail='Method "DELETE" not allowed')
