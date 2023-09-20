from django.utils import timezone
from django.db import models
from django.utils.translation import gettext_lazy as _
from PIL import Image
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
import os
from core import settings


def upload_to(instance, filename):
    return f'{filename}'

def validate_image_extension(value):
    """
    Custom validator to ensure that the uploaded file is a .jpg or .png image.
    """
    valid_extensions = ['.jpg', '.jpeg', '.png']
    ext = os.path.splitext(value.name)[1]  # Get the file extension
    if not ext.lower() in valid_extensions:
        raise ValidationError(_("Only .jpg and .png files are allowed."))


class Picture(models.Model):
    title = models.CharField(max_length=100)
    created = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(User, on_delete=models.PROTECT, related_name='images', blank=True)

    image = models.ImageField(_("Image"), upload_to=upload_to, validators=[validate_image_extension])
    image_200 = models.ImageField(upload_to=upload_to, blank=True, null=True)
    image_400 = models.ImageField(upload_to=upload_to, blank=True, null=True)
    

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.image:
            pil_image = Image.open(self.image.path)

            # Create a 400px height thumbnail
            if pil_image.height > 400:
                width = pil_image.width * 400 // pil_image.height
                pil_image.thumbnail((width, 400), Image.LANCZOS)
                thumbnail_400_path = self.image.path.replace(".jpg", "_400.jpg").replace(".png", "_400.png")
                pil_image.save(thumbnail_400_path)

                # Update the reference to the 400x400 thumbnail
                self.image_400 = os.path.relpath(thumbnail_400_path, settings.MEDIA_ROOT)

           # Create a 200px height thumbnail
            if pil_image.height > 200:
                width = pil_image.width * 200 // pil_image.height
                pil_image.thumbnail((width, 200), Image.LANCZOS)
                thumbnail_200_path = self.image.path.replace(".jpg", "_200.jpg").replace(".png", "_200.png")
                pil_image.save(thumbnail_200_path)

                # Update the reference to the 200x200 thumbnail
                self.image_200 = os.path.relpath(thumbnail_200_path, settings.MEDIA_ROOT)


class Profile(models.Model):

    MEMBERSHIP = (
        ('BASIC', 'Basic'),
        ('PREMIUM', 'Premium'),
        ('ENTERPRISE', 'Enterprise')
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    membership = models.CharField(max_length=10, choices=MEMBERSHIP, default='BASIC')

    def __str__(self):
        return f'{self.user.username} {self.membership} Profile'
    