from django.db import models
from django.utils.translation import gettext_lazy as _


def upload_to(instance, filename):
    return f'images/{filename}'

class Picture(models.Model):
    title = models.CharField(max_length=100)
    image = models.ImageField(_("Image"), upload_to=upload_to)
