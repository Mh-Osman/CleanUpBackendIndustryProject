# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib.auth import get_user_model
User = get_user_model()
from chat.models import Message, OneToOneChat, OneToOneChatmassage

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
from rest_framework.response import Response
from rest_framework.decorators import api_view
from django.db.models import Q
from chat.models import OneToOneChat, OneToOneChatmassage


@api_view(['GET'])
def load_message(request):
    user = request.user
    friend_email = request.query_params.get('friend_email')
    page = int(request.query_params.get('page', 1))   # default page 1
    limit = int(request.query_params.get('limit', 20))  # per page 20 messages

    if not friend_email:
        return Response({"error": "friend_email parameter is required."}, status=400)

    try:
        friend = User.objects.get(email=friend_email)
        chat = OneToOneChat.objects.filter(
            (Q(user1=user) & Q(user2=friend)) | (Q(user1=friend) & Q(user2=user))
        ).first()

        if not chat:
            return Response({"messages": []})

        # Get total messages count
        total_messages = OneToOneChatmassage.objects.filter(chat=chat).count()

        # Pagination logic
        start = (page - 1) * limit
        end = start + limit

        messages = (
            OneToOneChatmassage.objects.filter(chat=chat)
            .order_by('-timestamp')[start:end]
        )

        message_data = [
            {
                "id": msg.id,
                "sender": msg.sender.email,
                "content": msg.content,
                "timestamp": msg.timestamp.isoformat(),
                "image_url": msg.image_url,
                "file_url": msg.file_url,
            }
            for msg in messages
        ]

        # Send total + pagination info
        return Response({
            "page": page,
            "limit": limit,
            "total_messages": total_messages,
            "messages": list(reversed(message_data))  # latest at bottom
        })

    except User.DoesNotExist:
        return Response({"error": "Friend not found."}, status=404)
