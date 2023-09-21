import os
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


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


# Thumbnail size model
class Size(models.Model):
    width = models.IntegerField()
    height = models.IntegerField()

    def __str__(self):
        return f'{self.width}x{self.height}'


# User's Tier model
class Tier(models.Model):
    name = models.CharField(max_length=100)
    thumbnail_sizes = models.ManyToManyField(to=Size, related_name='tiers')
    has_original_link = models.BooleanField(default=False)
    can_generate_expiring_links = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    tier = models.ForeignKey(Tier, on_delete=models.PROTECT, related_name='profiles')  # Use ForeignKey to Tier model

    def __str__(self):
        return f'{self.user.username} - {self.tier.name}'
    

# Image model
class Image(models.Model):
    title = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(_("Image"), upload_to=upload_to, validators=[validate_image_extension])
    created_at = models.DateTimeField(auto_now_add=True)
    size = models.ForeignKey(Size, on_delete=models.PROTECT, related_name='images', blank=True, null=True)

    def __str__(self):
        return self.title

