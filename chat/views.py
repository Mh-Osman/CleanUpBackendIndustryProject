# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage

class UploadFileViewFromGroup(APIView):
    parser_classes = [MultiPartParser]  # ফাইল/ইমেজ আপলোডের জন্য

    def post(self, request, format=None):
        image = request.FILES.get('image')  # ইমেজ ফাইল
        file = request.FILES.get('file')    # সাধারণ ফাইল

        # ইমেজ এবং ফাইল সংরক্ষণ
        image_path = default_storage.save(f'chat/images/{image.name}', image) if image else None
        file_path = default_storage.save(f'chat/files/{file.name}', file) if file else None

        # URL তৈরি (যদি ফাইল সংরক্ষণ করা হয়)
        image_url = default_storage.url(image_path) if image_path else None
        file_url = default_storage.url(file_path) if file_path else None

        return Response({
            "image_url": image_url,
            "file_url": file_url,
            "message": "Upload successful"
        })

class UploadFileViewFromOneToOne(APIView):
    parser_classes = [MultiPartParser]  # ফাইল/ইমেজ আপলোডের জন্য

    def post(self, request, format=None):
        image = request.FILES.get('image')  # ইমেজ ফাইল
        file = request.FILES.get('file')    # সাধারণ ফাইল

        # ইমেজ এবং ফাইল সংরক্ষণ
        image_path = default_storage.save(f'chat/images/private/{image.name}', image) if image else None
        file_path = default_storage.save(f'chat/files/private/{file.name}', file) if file else None

        # URL তৈরি (যদি ফাইল সংরক্ষণ করা হয়)
        image_url = default_storage.url(image_path) if image_path else None
        file_url = default_storage.url(file_path) if file_path else None

        return Response({
            "image_url": image_url,
            "file_url": file_url,
            "message": "Upload successful"
        })
    