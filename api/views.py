import os
from io import BytesIO
from mimetypes import guess_type
from PIL import Image as PILImage
from rest_framework import viewsets, permissions, status, generics
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.decorators import api_view, permission_classes
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
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


class ImageView(generics.ListCreateAPIView):
    
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

    
        # Get the image dimensions
        image = serializer.validated_data['image']
        width, height = get_image_dimensions(image)

        # Get Size instance with image sizes if exists, else create new
        if Size.objects.filter(width=width, height=height):
            size_instance = Size.objects.get(width=width, height=height)
        else:
            size_instance = Size.objects.create(width=width, height=height)

        # Create Image instance from original image
        image_instance = self.save_original_image(image, serializer.validated_data['title'], size_instance)
        
        # Create and save thumbnails
        thumbnail_instances = self.create_and_save_thumbnails(image, thumbnail_sizes)

        # Create a Response dictionary with links to all resolutions
        response_data = self.create_response(serializer.data, image_instance, thumbnail_instances, width, height)

        headers = self.get_success_headers(serializer.data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


    def create_response(self, serializer_data, image_instance, thumbnail_instances, width, height):
        """
        Return response to be send to the user

            Parameters:
                    serializer_data (dict): Serialized request data from User
                    image_instance : image file
                    thumbnail_instances (list): List of Image instances
                    width (int): Original image width
                    height (int): Original image height

            Returns:
                    response_data (dict): Response to the User
        """
        response_data = serializer_data

        # If user's tier allow to have link to original image
        if self.request.user.profile.tier.has_original_link:
            # Add path to original size
            response_data['image'] = image_instance.image.url
            # Add size of original image
            response_data['size'] = {'width': width, 'height': height}
        else:
        # Delete keys if not
            del response_data['image']
            del response_data['size']

        # Add paths to all created thumbnails
        for instance in thumbnail_instances:
            response_data[f'image_{instance.size}'] = f"{MEDIA_URL}{instance.image.name}"

        return response_data


    def create_and_save_thumbnails(self, image, thumbnail_sizes):
        """
        Return list of created Image instances 

            Parameters:
                    image: image file
                    thumbnails_sizes(iter): Queryset of Size objects in Tier's thumbnails_sizes field

            Returns:
                    thumbnail_instances (list): List of Image instances
        """

        thumbnail_instances = []

        for size in thumbnail_sizes:
            thumbnail = self.create_thumbnail(image, size)
            # Create a name with pattern - 'thumbnail_<width>x<height>_<image_name>'
            thumbnail_name = f"thumbnail_{size.width}x{size.height}_{image.name}"

            tmp_thumbnail = BytesIO()
            thumbnail.save(tmp_thumbnail, format='JPEG' if image.name.lower().endswith('.jpg') else 'PNG')
            
            # Create Image instance
            thumbnail_instance = Image(
                                    title=thumbnail_name,
                                    user=self.request.user,
                                    size=size,
            )

            # Add image file to instance
            thumbnail_instance.image.save(thumbnail_name, tmp_thumbnail, save=False)

            # Save instance
            thumbnail_instance.save()

            # Add instance to returned list
            thumbnail_instances.append(thumbnail_instance)

        return thumbnail_instances


    def save_original_image(self, image, title, size):
        """
        Return Image instance of original image

            Parameters:
                    image: image file
                    title (str): Title of image
                    size (obj): Size instance

            Returns:
                    image_instance (obj): Image instance
        """
        # Create Image instance
        image_instance = Image(title=title,
                               user=self.request.user,
                               size=size
                              )
        # Add image file to instance
        image_instance.image.save(image.name, image, save=False)

        # Save instance in db
        if self.request.user.profile.tier.has_original_link:
            image_instance.save()

        return image_instance


    def create_thumbnail(self, image_file, size):
        """
        Return resized image

            Parameters:
                    image: image file
                    size (obj): Size object

            Returns:
                    img (obj): Resized image as PIL.Image object
        """
        try:
            img = PILImage.open(image_file)

            # Create thumbnail with set height and proportional width
            img.thumbnail((img.width * size.height // size.width, size.height), PILImage.LANCZOS)

            return img
        
        except Exception as e:
            print(f'-----{e}------')
            return e

