from django.shortcuts import render
from rest_framework import viewsets, generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from .serializers import PictureBasicUserSerializer, PicturePremiumUserSerializer
from .models import Picture


# class PictureView(APIView):
#     # permission_classes = [permissions.IsAuthenticated]
#     permission_classes = [permissions.AllowAny]
#     parser_classes = [MultiPartParser, FormParser]

#     def post(self, request, format=None):
#         print(request.data)
#         serializer = PictureSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PictureViewSet(viewsets.ModelViewSet):

    # queryset = Picture.objects.none()
    # serializer_class = PictureBasicUserSerializer
    queryset = Picture.objects.all()  # Use .all() to get all Picture objects
    serializer_class = PictureBasicUserSerializer
    permission_classes = [permissions.IsAuthenticated]  # Add authentication permission

    def get_queryset(self):
        return Picture.objects.filter(author=self.request.user)

    def get_user(self):
        
        user = self.request.user
        return user
    
    def get_serializer_class(self):
        user = self.request.user
        print(self.request.user.profile.membership)
        if user.profile.membership == 'BASIC':
            return PictureBasicUserSerializer
        elif user.profile.membership == 'PREMIUM':
            return PicturePremiumUserSerializer
        return PictureBasicUserSerializer  # Return a default serializer if membership is not recognized
    
    # def get_serializer_class(self):
        
    #     user = self.get_user()
    #     if user.profile.membership == 'Basic':
    #         return PictureBasicUserSerializer
    #     if user.profile.membership == 'Premium':
    #         return PicturePremiumUserSerializer
    
    # def get_queryset(self):

    #     user = self.get_user()
    #     return Picture.objects.filter(author=user)
    
    # def create(self, request):
    #     # super().create(request)
    #     print(request.data)
    #     # serializer = PictureSerializer(data=request.data)
    #     if serializer_class.is_valid():
    #         serializer_class.save()
    #         return Response(serializer_class.data, status=status.HTTP_200_OK)
    #     else:
    #         return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)

    # def create(self, request, *args, **kwargs):
    #     serializer_class = self.get_serializer_class()
    #     serializer = serializer_class(data=request.data)

    #     if serializer.is_valid():
    #         serializer.save(author=request.user)  # Assign the author to the current user
    #         return Response(serializer.data, status=status.HTTP_201_CREATED)
    #     else:
    #         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
