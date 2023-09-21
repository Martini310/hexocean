from django.contrib import admin
from api.models import Tier, Size, Image, Profile, TemporaryLink

admin.site.register(Tier)
admin.site.register(Size)
admin.site.register(Image)
admin.site.register(Profile)
admin.site.register(TemporaryLink)
