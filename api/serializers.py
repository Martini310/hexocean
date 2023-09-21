from rest_framework import serializers
from .models import Image, Tier, Size


class ImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Image
        fields = ('title', 'image', 'size')


class TierSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tier
        fields = ('name', 'thumbnail_sizes')


class SizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Size
        fields = ('width', 'height')
