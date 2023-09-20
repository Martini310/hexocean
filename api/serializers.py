from rest_framework import serializers
from .models import Picture


# class PictureSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Picture
#         fields = ('id', 'title', 'author', 'image')


# class PictureBasicUserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Picture
#         fields = ('author', 'title', 'image_200')


# class PicturePremiumUserSerializer(serializers.ModelSerializer):

#     class Meta:
#         model = Picture
#         fields = ('author', 'title', 'image_200', 'image_400', 'image')

class PictureBasicUserSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Picture
        fields = ('author', 'title', 'image_200')

class PicturePremiumUserSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Picture
        fields = ('author', 'title', 'image_200', 'image_400', 'image')
