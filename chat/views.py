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

@api_view(['GET'])
def load_message_from_all_chat(request):
    user = request.user
    page = int(request.query_params.get('page', 1))   # default page 1
    limit = int(request.query_params.get('limit', 20))  # per page 20 messages

    # Get total messages count
    total_messages = OneToOneChatmassage.objects.filter(
        Q(chat__user1=user) | Q(chat__user2=user)
    ).count()

    # Pagination logic
    start = (page - 1) * limit
    end = start + limit

    messages = (
        OneToOneChatmassage.objects.filter(
            Q(chat__user1=user) | Q(chat__user2=user)
        )
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
            "login_user": user.email,
        }
        for msg in messages
    ]

    # Send total + pagination info
    return Response({
        "page": page,
        "limit": limit,
        "total_messages": total_messages,
        "messages": list(reversed(message_data)),  # latest at bottom
        
    })


from plan.models import Subscription
from assign_task_employee.models import SpecialServicesModel
# @api_view(['GET'])
# def connected_users(request):
#     user = request.user
#     chats = OneToOneChat.objects.filter(Q(user1=user) | Q(user2=user))
#     connected_users_list = []
    
#     for chat in chats:
#         friend = chat.user2 if chat.user1 == user else chat.user1
#         connected_users_list.append({
#             "email": friend.email,
#             "name": friend.name,    
#         })

#     return Response({"connected_users": connected_users_list})# urls.py 

# @api_view(['GET'])
# def connected_users(request):
#     user = request.user
#     all_subscriptions = Subscription.objects.filter(user=user, status="active")
#     allow_chat_users = set()
#     allow_chat_users.add(user)
#     if user.user_type == 'client':
#         for subscription in all_subscriptions:
#             employees = subscription.employee.all()
#             for emp in employees:
#                 allow_chat_users.add(emp)
#     elif user.user_type in ['employee', 'supervisor']:
#         for subscription in all_subscriptions:
#             client = subscription.user
#             allow_chat_users.add(client)

#     all_special_services = SpecialServicesModel.objects.filter(worker=user, status__in=["pending", "started"])
#     if user.user_type == 'client':
#         for service in all_special_services:
#             allow_chat_users.add(service.worker)
#     elif user.user_type in ['employee', 'supervisor']:
#         for service in all_special_services:

#             allow_chat_users.add(service.apartment.first().client)
  
#     chats = OneToOneChat.objects.filter(Q(user1=user) | Q(user2=user))
#     connected_users_list = []
#     for chat in chats:
#         friend = chat.user2 if chat.user1 == user else chat.user1
#         if friend  in allow_chat_users:
#             connected_users_list.append({
#                 "email": friend.email,
#                 "name": friend.name,    
#             })
#             allow_chat_users.discard(friend)
#         else:
#             connected_users_list.append({
#                 "email": friend.email,
#                 "name": friend.name,    
#             })

#     return Response({"connected_users": connected_users_list,
#                       "allowed_users_not_connected": [
#                          {"email": u.email, "name": u.name} for u in allow_chat_users if u != user
#                      ]
#                     })


# from rest_framework.decorators import api_view, permission_classes
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from django.db.models import Q

# from plan.models import Subscription
# from assign_task_employee.models import SpecialServicesModel
# from chat.models import OneToOneChat

# from django.contrib.auth import get_user_model
# User = get_user_model()

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def connected_users(request):
#     user = request.user

#     # -----------------------------
#     # Get active subscriptions
#     # -----------------------------
#     all_subscriptions = Subscription.objects.filter(user=user, status="active").prefetch_related('employee')
#     allow_chat_users = set()
#     allow_chat_users.add(user)

#     subscription_data_map = {}  # user -> subscription info

#     if user.user_type == 'client':
#         for subscription in all_subscriptions:
#             for emp in subscription.employee.all():
#                 allow_chat_users.add(emp)
#                 subscription_data_map[emp] = {
#                     "id": subscription.id,
#                     "name": getattr(subscription.plan, "name", None),
#                     "building": getattr(subscription.building, "name", None),
#                     "region": getattr(subscription.region, "name", None)
#                 }
#     elif user.user_type in ['employee', 'supervisor']:
#         for subscription in all_subscriptions:
#             client_user = subscription.user
#             allow_chat_users.add(client_user)
#             subscription_data_map[client_user] = {
#                 "id": subscription.id,
#                 "name": getattr(subscription.plan, "name", None),
#                 "building": getattr(subscription.building, "name", None),
#                 "region": getattr(subscription.region, "name", None)
#             }

#     # -----------------------------
#     # Get special services
#     # -----------------------------
#     all_special_services = SpecialServicesModel.objects.filter(
#         Q(worker=user) | Q(apartment__special_services_apartments__worker=user),
#         status__in=["pending", "started"]
#     ).distinct().prefetch_related('building', 'region')

#     special_service_data_map = {}  # user -> special service info

#     if user.user_type == 'client':
#         for service in all_special_services:
#             allow_chat_users.add(service.worker)
#             special_service_data_map[service.worker] = {
#                 "id": service.id,
#                 "name": service.name,
#                 "region": getattr(service.region, "name", None),
#                 "building": getattr(service.building, "name", None),
               
#             }

#     elif user.user_type in ['employee', 'supervisor']:
#         for service in all_special_services:
#             for apt in service.apartment.all():
#                 client_user = getattr(apt, "client", None)
#                 if client_user:
#                     allow_chat_users.add(client_user)
#                     special_service_data_map[client_user] = {
#                         "id": service.id,
#                         "name": service.name,
#                         "region": getattr(service.region, "name", None),
#                         "building": getattr(service.building, "name", None),
                     
#                     }

#     # -----------------------------
#     # Get one-to-one chats
#     # -----------------------------
#     chats = OneToOneChat.objects.filter(Q(user1=user) | Q(user2=user))
#     connected_users_list = []

#     for chat in chats:
#         friend = chat.user2 if chat.user1 == user else chat.user1
#         data = {
#             "email": friend.email,
#             "name": getattr(friend, "name", friend.name),
#             "subscription": subscription_data_map.get(friend),
#             "special_service": special_service_data_map.get(friend)
#         }
#         connected_users_list.append(data)
#         allow_chat_users.discard(friend)

#     # Remaining allowed users not connected
#     allowed_users_not_connected = [
#         {
#             "email": u.email,
#             "name": getattr(u, "name", u.name),
#             "subscription": subscription_data_map.get(u),
#             "special_service": special_service_data_map.get(u)
#         }
#         for u in allow_chat_users if u != user
#     ]

#     return Response({
#         "connected_users": connected_users_list,
#         "allowed_users_not_connected": allowed_users_not_connected
#     })



from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.db.models import Q, Max
from django.utils import timezone

from plan.models import Subscription
from assign_task_employee.models import SpecialServicesModel
from chat.models import OneToOneChat, OneToOneChatmassage
from django.contrib.auth import get_user_model
User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def connected_users(request):
    user = request.user

    # -----------------------------
    # Get active subscriptions
    # -----------------------------
    all_subscriptions = Subscription.objects.filter(user=user, status="active").prefetch_related('employee')
    allow_chat_users = set()
    allow_chat_users.add(user)
    subscription_data_map = {}  # user -> subscription info

    if user.user_type == 'client':
        for subscription in all_subscriptions:
            for emp in subscription.employee.all():
                allow_chat_users.add(emp)
                subscription_data_map[emp] = {
                    "id": subscription.id,
                    "name": getattr(subscription.plan, "name", None),
                    "building": getattr(subscription.building, "name", None),
                    "region": getattr(subscription.region, "name", None),
                    # "asdigned_date":getattr(subscription.created_at, "name", None)
                }
    elif user.user_type in ['employee', 'supervisor']:
        for subscription in all_subscriptions:
            client_user = subscription.user
            allow_chat_users.add(client_user)
            subscription_data_map[client_user] = {
                "id": subscription.id,
                "name": getattr(subscription.plan, "name", None),
                "building": getattr(subscription.building, "name", None),
                "region": getattr(subscription.region, "name", None)
            }

    # -----------------------------
    # Get special services
    # -----------------------------
    all_special_services = SpecialServicesModel.objects.filter(
        Q(worker=user) | Q(apartment__special_services_apartments__worker=user),
        status__in=["pending", "started"]
    ).distinct().prefetch_related('building', 'region')

    special_service_data_map = {}  # user -> special service info

    if user.user_type == 'client':
        for service in all_special_services:
            allow_chat_users.add(service.worker)
            special_service_data_map[service.worker] = {
                "id": service.id,
                "name": service.name,
                "region": getattr(service.region, "name", None),
                "building": getattr(service.building, "name", None),
            }

    elif user.user_type in ['employee', 'supervisor']:
        for service in all_special_services:
            for apt in service.apartment.all():
                client_user = getattr(apt, "client", None)
                if client_user:
                    allow_chat_users.add(client_user)
                    special_service_data_map[client_user] = {
                        "id": service.id,
                        "name": service.name,
                        "region": getattr(service.region, "name", None),
                        "building": getattr(service.building, "name", None),
                    }

    # -----------------------------
    # Get one-to-one chats and latest message
    # -----------------------------
    chats = OneToOneChat.objects.filter(Q(user1=user) | Q(user2=user)).prefetch_related('user1', 'user2')
    user_dict = {}  # email -> user data

    for chat in chats:
        friend = chat.user2 if chat.user1 == user else chat.user1
        # Get the most recent message
        last_message = OneToOneChatmassage.objects.filter(chat=chat).order_by('-timestamp').first()
        last_message_data = None
        if last_message:
            last_message_data = {
                "content": last_message.content,
                "image_url": last_message.image_url,
                "file_url": last_message.file_url,
                "timestamp": last_message.timestamp
            }

        user_dict[friend.email] = {
            "email": friend.email,
            "name": getattr(friend, "name", friend.username),
            "subscription": subscription_data_map.get(friend),
            "special_service": special_service_data_map.get(friend),
            "status": "connected",
            "last_message": last_message_data,
            "last_chat": last_message.timestamp if last_message else None
        }
        allow_chat_users.discard(friend)

    # Remaining allowed users not connected
    for u in allow_chat_users:
        if u == user:
            continue
        user_dict[u.email] = {
            "email": u.email,
            "name": getattr(u, "name", u.username),
            "subscription": subscription_data_map.get(u),
            "special_service": special_service_data_map.get(u),
            "status": "not_connected",
            "last_message": None,
            "last_chat": None
        }
     
    # Sort by recent message timestamp
    # Define a helper to make all datetimes aware
    def make_aware(dt):
        if dt is None:
            return timezone.datetime.min.replace(tzinfo=timezone.get_current_timezone())
        if timezone.is_naive(dt):
            return timezone.make_aware(dt, timezone.get_current_timezone())
        return dt

    # Sort users by recent message timestamp
    all_users_sorted = sorted(
        user_dict.values(),
        key=lambda x: make_aware(x.get("last_chat")),
        reverse=True
        )
    # Remove last_chat field before sending to client
    for u in all_users_sorted:
        u.pop("last_chat", None)

    return Response({
        "users": all_users_sorted
    })
