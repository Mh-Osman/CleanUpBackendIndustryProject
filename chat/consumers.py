import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from django.utils import timezone
from .models import Group, Message, GroupMembership


# class GroupChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.group_id_str = self.scope['url_route']['kwargs']['group_id']
#         self.group_name = self.scope['url_route']['kwargs']['group_name']
#         # admin_id যদি URL-এ থাকে (routing.py-এ define করতে হবে)
#         self.admin_id = self.scope['url_route']['kwargs'].get('admin_id')

#         @database_sync_to_async
#         def get_or_create_group():
#             from django.core.exceptions import ObjectDoesNotExist
#             try:
#                 if self.group_id_str == '0':
#                     # নতুন গ্রুপ বানাতে admin_id দরকার
#                     if not self.admin_id:
#                         return None
#                     admin_user = User.objects.get(id=self.admin_id)
#                     return Group.objects.create(name=self.group_name, admin=admin_user)
#                 else:
#                     group_id = int(self.group_id_str)
#                     return Group.objects.get(id=group_id)
#             except (ObjectDoesNotExist, ValueError):
#                 return None

#         group = await get_or_create_group()

#         if not group:
#             # Accept connection so we can send error JSON, তারপর close
#             await self.accept()
#             await self.send(text_data=json.dumps({
#                 "status": "error",
#                 "message": "Invalid group ID or admin ID not provided"
#             }))
#             await self.close()
#             return

#         self.group_id = group.id
#         self.group_name = group.name
#         self.room_group_name = f"group_{self.group_id}"

#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#         # Connection success
#         await self.send(text_data=json.dumps({
#             "status": "connected",
#             "group_id": self.group_id,
#             "group_name": self.group_name
#         }))

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     async def receive(self, text_data=None, bytes_data=None):
#         if not text_data:
#             await self.send(json.dumps({"status": "error", "message": "No data received"}))
#             return

#         try:
#             data = json.loads(text_data)
#         except json.JSONDecodeError:
#             await self.send(json.dumps({"status": "error", "message": "Invalid JSON"}))
#             return

#         action = data.get('action')

#         if action == "join":
#             await self.handle_join(data)
#         elif action == "leave":
#             await self.handle_leave(data)
#         elif action == "message":
#             await self.handle_message(data)
#         elif action == "add_admin":
#             await self.handle_add_admin(data)
#         elif action == "load_messages":
#             await self.handle_load_messages(data)
#         else:
#             await self.send(json.dumps({"status": "error", "message": "Invalid action"}))

#     # -------- Join ----------
#     async def handle_join(self, data):
#         user_id = data.get('user_id')
#         if not user_id:
#             await self.send(json.dumps({"status": "error", "message": "user_id is required"}))
#             return

#         @database_sync_to_async
#         def add_user_to_group():
#             try:
#                 user = User.objects.get(id=user_id)
#                 group = Group.objects.get(id=self.group_id)
#                 membership, created = GroupMembership.objects.get_or_create(user=user, group=group)
#                 return created, user
#             except (User.DoesNotExist, Group.DoesNotExist):
#                 return False, None

#         created, user = await add_user_to_group()
#         if created:
#             await self.send(text_data=json.dumps({"status": "success", "message": f"{user.username} joined the group"}))
#         else:
#             await self.send(text_data=json.dumps({"status": "error", "message": "User already in group or invalid"}))

#     # -------- Leave ----------
#     async def handle_leave(self, data):
#         user_id = data.get('user_id')
#         if not user_id:
#             await self.send(json.dumps({"status": "error", "message": "user_id is required"}))
#             return

#         @database_sync_to_async
#         def remove_user_from_group():
#             try:
#                 user = User.objects.get(id=user_id)
#                 deleted_count, _ = GroupMembership.objects.filter(user=user, group_id=self.group_id).delete()
#                 return deleted_count, user
#             except (User.DoesNotExist, Group.DoesNotExist):
#                 return 0, None

#         deleted_count, user = await remove_user_from_group()
#         if deleted_count:
#             await self.send(json.dumps({"status": "success", "message": f"{user.username} left the group"}))
#         else:
#             await self.send(json.dumps({"status": "error", "message": "User not in group or invalid"}))

#     # -------- Add admin ----------
#     async def handle_add_admin(self, data):
#         user_id = data.get('user_id')
#         if not user_id:
#             await self.send(json.dumps({"status": "error", "message": "user_id is required"}))
#             return

#         @database_sync_to_async
#         def add_admin_to_group():
#             try:
#                 user = User.objects.get(id=user_id)
#                 group = Group.objects.get(id=self.group_id)
#                 group.admin = user
#                 group.save()
#                 return True, user
#             except (User.DoesNotExist, Group.DoesNotExist):
#                 return False, None

#         success, user = await add_admin_to_group()
#         if success:
#             await self.send(text_data=json.dumps({"status": "success", "message": f"{user.username} is now the admin of the group"}))
#         else:
#             await self.send(text_data=json.dumps({"status": "error", "message": "Failed to set admin. User or group may be invalid."}))

#     # -------- Send message ----------
#     async def handle_message(self, data):
#         message = data.get('message', '').strip()
#         user_id = data.get('user_id')
#         if not message or not user_id:
#             await self.send(json.dumps({"status": "error", "message": "message and user_id are required"}))
#             return

#         @database_sync_to_async
#         def save_message():
#             try:
#                 user = User.objects.get(id=user_id)
#                 group = Group.objects.get(id=self.group_id)
#                 if not GroupMembership.objects.filter(user=user, group=group).exists():
#                     return None
#                 return Message.objects.create(sender=user, content=message, group=group)
#             except (User.DoesNotExist, Group.DoesNotExist):
#                 return None

#         saved_message = await save_message()
#         if not saved_message:
#             await self.send(json.dumps({"status": "error", "message": "User not authenticated or not a member"}))
#             return

#         # Timestamp to UTC ISO
#         ts = saved_message.timestamp
#         # ensure aware: if naive, make it aware using current timezone
#         try:
#             ts_iso = ts.astimezone(timezone.utc).isoformat()
#         except Exception:
#             ts_iso = timezone.localtime(ts).isoformat()

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 'type': 'chat_message',
#                 'message': saved_message.content,
#                 'timestamp': ts_iso,
#                 'sender_username': saved_message.sender.username
#             }
#         )

#     # -------- Load previous messages ----------
#     async def handle_load_messages(self, data):
#         # frontend can send {"action":"load_messages", "limit": 50}
#         try:
#             limit = int(data.get("limit", 20))
#         except Exception:
#             limit = 20
#         if limit <= 0:
#             limit = 20

#         @database_sync_to_async
#         def get_recent_messages():
#             try:
#                 group = Group.objects.get(id=self.group_id)
#                 msgs = Message.objects.filter(group=group).order_by('-timestamp')[:limit]
#                 result = []
#                 for msg in reversed(msgs):  # chronological order
#                     # safe timestamp to UTC iso
#                     try:
#                         ts = msg.timestamp.astimezone(timezone.utc).isoformat()
#                     except Exception:
#                         ts = timezone.localtime(msg.timestamp).isoformat()
#                     result.append({
#                         "id": msg.id,
#                         "sender": msg.sender.username,
#                         "content": msg.content,
#                         "timestamp": ts
#                     })
#                 return result
#             except Group.DoesNotExist:
#                 return []

#         messages = await get_recent_messages()
#         await self.send(text_data=json.dumps({"status": "history", "messages": messages}))

#     # -------- Broadcast handler ----------
#     async def chat_message(self, event):
#         await self.send(text_data=json.dumps({
#             'message': event['message'],
#             'timestamp': event['timestamp'],
#             'sender_username': event['sender_username']
#         }))
from django.contrib.auth.models import AnonymousUser


import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from django.contrib.auth.models import AnonymousUser
from .models import Group, Message, GroupMembership


# class GroupChatConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         # Extract user from JWT (via middleware)
#         self.user = self.scope.get("user", AnonymousUser())

#         if not self.user or self.user.is_anonymous:
#             await self.close()
#             return

#         self.group_id_str = self.scope["url_route"]["kwargs"]["group_id"]
#         self.group_name = self.scope["url_route"]["kwargs"]["group_name"]

#         # Validate or create group
#         group = await self.get_or_create_group()
#         if not group:
#             await self.accept()
#             await self.send(text_data=json.dumps({
#                 "status": "error",
#                 "message": "Invalid group ID or admin ID not provided"
#             }))
#             await self.close()
#             return

#         self.group = group
#         self.group_id = group.id
#         self.room_group_name = f"group_{self.group_id}"

#         # Join room group
#         await self.channel_layer.group_add(self.room_group_name, self.channel_name)
#         await self.accept()

#         await self.send(text_data=json.dumps({
#             "status": "connected",
#             "user": self.user.username,
#             "group_id": self.group_id,
#             "group_name": self.group_name
#         }))

#     # --- Database helper
#     @database_sync_to_async
#     def get_or_create_group(self):
#         from django.core.exceptions import ObjectDoesNotExist
#         try:
#             group_id = int(self.group_id_str)
#             return Group.objects.get(id=group_id)
#         except (ObjectDoesNotExist, ValueError):
#             return None

#     # --- Disconnect
#     async def disconnect(self, close_code):
#         if hasattr(self, "room_group_name"):
#             await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

#     # --- Message receiver
#     async def receive(self, text_data=None, bytes_data=None):
#         if not text_data:
#             await self.send(json.dumps({"status": "error", "message": "No data received"}))
#             return

#         try:
#             data = json.loads(text_data)
#         except json.JSONDecodeError:
#             await self.send(json.dumps({"status": "error", "message": "Invalid JSON"}))
#             return

#         action = data.get("action")

#         if action == "join":
#             await self.handle_join()
#         elif action == "leave":
#             await self.handle_leave()
#         elif action == "message":
#             await self.handle_message(data)
#         elif action == "add_admin":
#             await self.handle_add_admin(data)
#         elif action == "load_messages":
#             await self.handle_load_messages(data)
#         else:
#             await self.send(json.dumps({"status": "error", "message": "Invalid action"}))

#     # --- Join Group
#     async def handle_join(self):
#         @database_sync_to_async
#         def add_user_to_group():
#             try:
#                 membership, created = GroupMembership.objects.get_or_create(
#                     user=self.user, group=self.group
#                 )
#                 return created
#             except Exception:
#                 return False

#         created = await add_user_to_group()
#         if created:
#             await self.send(json.dumps({
#                 "status": "success",
#                 "message": f"{self.user.username} joined the group"
#             }))
#         else:
#             await self.send(json.dumps({
#                 "status": "error",
#                 "message": "Already in group"
#             }))

#     # --- Leave Group
#     async def handle_leave(self):
#         @database_sync_to_async
#         def remove_user_from_group():
#             try:
#                 deleted_count, _ = GroupMembership.objects.filter(
#                     user=self.user, group=self.group
#                 ).delete()
#                 return deleted_count
#             except Exception:
#                 return 0

#         deleted_count = await remove_user_from_group()
#         if deleted_count:
#             await self.send(json.dumps({
#                 "status": "success",
#                 "message": f"{self.user.username} left the group"
#             }))
#         else:
#             await self.send(json.dumps({
#                 "status": "error",
#                 "message": "User not in group"
#             }))

#     # --- Add admin
#     async def handle_add_admin(self, data):
#         target_user_id = data.get("user_id")

#         @database_sync_to_async
#         def add_admin():
#             try:
#                 target_user = self.user.__class__.objects.get(id=target_user_id)
#                 group = self.group
#                 if group.admin != self.user:
#                     return False, "Only admin can assign new admin"
#                 group.admin = target_user
#                 group.save()
#                 return True, target_user.username
#             except Exception:
#                 return False, None

#         success, username = await add_admin()
#         if success:
#             await self.send(json.dumps({
#                 "status": "success",
#                 "message": f"{username} is now the admin"
#             }))
#         else:
#             await self.send(json.dumps({
#                 "status": "error",
#                 "message": username or "Failed to add admin"
#             }))

#     # --- Send message
#     async def handle_message(self, data):
#         message_text = data.get("message", "").strip()
#         if not message_text:
#             await self.send(json.dumps({"status": "error", "message": "Message required"}))
#             return

#         @database_sync_to_async
#         def save_message():
#             try:
#                 if not GroupMembership.objects.filter(user=self.user, group=self.group).exists():
#                     return None
#                 return Message.objects.create(
#                     sender=self.user, content=message_text, group=self.group
#                 )
#             except Exception:
#                 return None

#         saved_message = await save_message()
#         if not saved_message:
#             await self.send(json.dumps({
#                 "status": "error",
#                 "message": "Not allowed to send message"
#             }))
#             return

#         ts = saved_message.timestamp
#         ts_iso = timezone.localtime(ts).isoformat()

#         await self.channel_layer.group_send(
#             self.room_group_name,
#             {
#                 "type": "chat_message",
#                 "message": saved_message.content,
#                 "timestamp": ts_iso,
#                 "sender_username": saved_message.sender.username
#             }
#         )

#     # --- Load messages
#     async def handle_load_messages(self, data):
#         limit = int(data.get("limit", 20))

#         @database_sync_to_async
#         def get_recent_messages():
#             msgs = Message.objects.filter(group=self.group).order_by("-timestamp")[:limit]
#             result = []
#             for msg in reversed(msgs):
#                 ts = timezone.localtime(msg.timestamp).isoformat()
#                 result.append({
#                     "id": msg.id,
#                     "sender": msg.sender.username,
#                     "content": msg.content,
#                     "timestamp": ts
#                 })
#             return result

#         messages = await get_recent_messages()
#         await self.send(json.dumps({"status": "history", "messages": messages}))

#     # --- Broadcast
#     async def chat_message(self, event):
#         await self.send(json.dumps({
#             "message": event["message"],
#             "timestamp": event["timestamp"],
#             "sender_username": event["sender_username"]
#         }))

"""3rd script"""
# # consumers.py
# from datetime import datetime
# from channels.generic.websocket import AsyncJsonWebsocketConsumer
# from django.contrib.auth.models import AnonymousUser
# from channels.db import database_sync_to_async
# from .models import Group, CoAdmin

# class GroupChatConsumer(AsyncJsonWebsocketConsumer):

#     async def connect(self):
#         self.user = self.scope.get("user", AnonymousUser())
#         if not self.user or self.user.is_anonymous:
#             await self.close()
#             return

#         await self.accept()
#         await self.send_json({
#             "status": "connected",
#             "user": self.user.username,
#         })

#     async def disconnect(self, close_code):
#         if hasattr(self, "group_name"):
#             await self.channel_layer.group_discard(self.group_name, self.channel_name)

#     async def receive_json(self, content, **kwargs):
#         action = content.get("action")
#         if action == "create_group":
#             await self.handle_create_group(content)
#         elif action == "join_group":
#             await self.handle_join_group(content)
#         elif action == "send_message":
#             await self.handle_send_message(content)
#         else:
#             await self.send_json({"error": "Invalid action"})

#     # -------------------------------
#     # Action handlers
#     # -------------------------------
#     async def handle_create_group(self, content):
#         group_name = content.get("group_name", "").strip()
#         if not group_name:
#             await self.send_json({"error": "Group name required"})
#             return

#         group, created = await self.get_or_create_group(group_name, self.user)

#         if created:
#             await self.send_json({
#                 "message": f"Group '{group_name}' created successfully",
#                 "admin": self.user.username
#             })
#         else:
#             await self.send_json({"message": f"Group '{group_name}' already exists"})

#         await self.channel_layer.group_add(group_name, self.channel_name)
#         self.group_name = group_name

#     async def handle_join_group(self, content):
#         group_name = content.get("group_name", "").strip()
#         if not group_name:
#             await self.send_json({"error": "Group name required"})
#             return

#         exists = await self.group_exists(group_name)
#         if not exists:
#             await self.send_json({"error": "Group does not exist"})
#             return

#         await self.channel_layer.group_add(group_name, self.channel_name)
#         self.group_name = group_name
#         await self.send_json({"message": f"Joined group '{group_name}'"})

#     async def handle_send_message(self, content):
#         if not hasattr(self, "group_name"):
#             await self.send_json({"error": "You must join a group first"})
#             return

#         message = content.get("message", "").strip()
#         if not message:
#             await self.send_json({"error": "Message cannot be empty"})
#             return
        
#         await self.channel_layer.group_send(
#             self.group_name,
#             {
#                 "type": "chat_message",
#                 "user": self.user.username,
#                 "message": message,
#                 "timestamp": datetime.utcnow().isoformat()
#             }
#         )

#     async def chat_message(self, event):
#         await self.send_json({
#             "sender_username": event["user"],
#             "message": event["message"],
#             "timestamp": event["timestamp"]
#         })

#     # -------------------------------
#     # Database helpers
#     # -------------------------------
#     @database_sync_to_async
#     def get_or_create_group(self, name, user):
#         group, created = Group.objects.get_or_create(
#             name=name,
#             defaults={"admin": user}
#         )
#         if created:
#             CoAdmin.objects.create(group=group, user=user)
#         return group, created

#     @database_sync_to_async
#     def group_exists(self, name):
#         return Group.objects.filter(name=name).exists()


# consumers.py
from datetime import datetime
from django.utils import timezone
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.contrib.auth.models import AnonymousUser
from channels.db import database_sync_to_async
from .models import Group, CoAdmin, GroupMembership, Message,OneToOneChat, OneToOneChatmassage

class GroupChatConsumer(AsyncJsonWebsocketConsumer):

    async def connect(self):
        # Get user from scope
        self.user = self.scope.get("user", AnonymousUser())
        if not self.user or self.user.is_anonymous:
            await self.close()
            return

        # Get group_name from URL
        self.group_name = self.scope["url_route"]["kwargs"]["group_name"]

        # Accept connection
        await self.accept()

        # Join the channel group
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        # Send confirmation to client
        await self.send_json({
            "status": "connected",
            "user": self.user.username,
            "group": self.group_name
        })

    async def disconnect(self, close_code):
        # Remove user from the group
        if hasattr(self, "group_name"):
            await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content, **kwargs):
        """
        Expects JSON with "action" key:
        - create_group
        - send_message
        """
        action = content.get("action")

        if action == "create_group":
            await self.handle_create_group()
        elif action == "send_message":
            await self.handle_send_message(content)
        elif action == "add_admin":
            await self.handle_add_co_admin(content)
        elif action == "join_group":
            await self.join_group(content)
        elif action == "leave_group":
            await self.leave_group(content)
        elif action == "load_messages":
            await self.load_messages(content)
        elif action == "delete_message":
            await self.delete_message(content)
        elif action == "edit_message":
            await self.edit_message(content)
        elif action == 'reply_message':
            await self.reply_message(content)

        elif action == "pin_message":
            await self.pin_message(content)
            
        else:
            await self.send_json({"error": "Invalid action"})

    # -------------------------------
    # Action handlers
    # -------------------------------
    async def handle_create_group(self):
        # Try to create the group in DB
        group, created = await self.get_or_create_group(self.group_name, self.user)

        if created:
            await self.send_json({
                "message": f"Group '{self.group_name}' created successfully",
                "admin": self.user.username
            })
        else:
            await self.send_json({
                "message": f"Group '{self.group_name}' already exists"
            })

    async def handle_send_message(self, content):
        message = content.get("message", "").strip()
        image_url = content.get("image_url")  # can be a file path or base64 string
        file_url = content.get("file_url")    # same

        # Validate: at least one content type
        if not message and not image_url and not file_url:
            await self.send_json({"error": "Message cannot be empty"})
            return

        # Check group existence
        if not await self.group_exists(self.group_name):
            await self.send_json({"error": "Group does not exist"})
            return

        # Save message to DB
        saved_message = await self.save_message_to_db(message, image_url, file_url)
        if not saved_message:
            await self.send_json({"error": "Failed to save message"})
            return

        await self.channel_layer.group_send(
        self.group_name,
        {
            "type": "chat_message",
            "user": self.user.username,
            "message": message,
            "image_url": image_url,
            "file_url": file_url,
            "timestamp": saved_message.timestamp.isoformat(),
        }
    )




    async def chat_message(self, event):
        # Send message to WebSocket clients
        await self.send_json({
            "sender_username": event["user"],
            "message": event.get("message"),
            "image_url": event.get("image_url"),
            "file_url": event.get("file_url"),
            "timestamp": event["timestamp"]
        })
    # -------------------------------
    # Add member as co-admin
    # -------------------------------
    async def handle_add_co_admin(self, content):
        new_member_username = content.get("username", "").strip()
        if not new_member_username:
            await self.send_json({"error": "Username required"})
            return

        # Synchronous DB operation wrapped in database_sync_to_async
        @database_sync_to_async
        def add_co_admin():
            try:
                user = User.objects.get(username=new_member_username)
                group = Group.objects.get(name=self.group_name)
                # Avoid duplicate co-admins
                if not CoAdmin.objects.filter(group=group, user=user).exists():
                    CoAdmin.objects.create(group=group, user=user)
                    print("CoAdmin created")
                    GroupMembership.objects.create(group=group, user=user)
                return True
            except Exception:
                return False

        success = await add_co_admin()
        if success:
            await self.send_json({
                "message": f"User '{new_member_username}' added as co-admin to group '{self.group_name}'"
            })
        else:
            await self.send_json({
                "error": "Failed to add co-admin. User or group may be invalid."
            })
    # -------------------------------
    # Join Group
    # -------------------------------
    async def join_group(self, content):
        group_name = content.get("group_name", "").strip()
        if not group_name:
            await self.send_json({"error": "Group name required"})
            return

        # Check if group exists in DB
        group_exists = await self.group_exists(group_name)
        if not group_exists:
            await self.send_json({"error": "Group does not exist"})
            return

        # Add user to the group in database
        success = await self.add_user_to_group(group_name, self.user)
        if success:
            await self.send_json({
                "message": f"User '{self.user.username}' joined group '{group_name}'"
            })
        else:
            await self.send_json({
                "error": f"User '{self.user.username}' is already a member of '{group_name}'"
            })

    # -------------------------------
    # Leave Group
    # -------------------------------

    async def leave_group(self, content):
        # Check if the user has joined any group in this WebSocket session
        if not hasattr(self, "group_name"):
            await self.send_json({
                "error": "You are not currently in any group."
            })
            return

        success = await self.remove_user_from_group(self.group_name, self.user)

        if success:
            # Remove user from channel layer group too
            await self.channel_layer.group_discard(self.group_name, self.channel_name)
            
            await self.send_json({
                "message": f"User '{self.user.username}' left group '{self.group_name}'"
            })

            # Optionally remove the group_name reference from this WebSocket session
            del self.group_name
        else:
            await self.send_json({
                "error": f"User '{self.user.username}' is not a member of '{self.group_name}'"
            })

     
    # ---------------------------
    # Load Messages (with pagination)
    # ---------------------------
    async def load_messages(self, content):
        limit = int(content.get("limit", 20))
        offset = int(content.get("offset", 0))

        # ✅ Call the sync DB function safely
        messages = await self.load_messages_func(self.group_name, limit, offset)

        message_list = [
            {
                "id": msg.id,
                "sender": msg.sender.username,
                "content": msg.content,
                "timestamp": timezone.localtime(msg.timestamp).isoformat(),
            }
            for msg in messages
        ]

        await self.send_json({
            "status": "history",
            "count": len(message_list),
            "limit": limit,
            "offset": offset,
            "messages": message_list,
        })
    
    # ---------------------------
    # Delete Message
    # ---------------------------
    async def delete_message(self, content):
        message_id = content.get("message_id")
        if not message_id:
            await self.send_json({"error": "message_id is required"})
            return

        @database_sync_to_async
        def delete_message_from_db():
            try:
                message = Message.objects.get(id=message_id, group__name=self.group_name)
                if message.sender != self.user:
                    return False  # Only sender can delete their message
                message.delete()
                return True
            except Message.DoesNotExist:
                return False

        success = await delete_message_from_db()
        if success:
            await self.send_json({
                "message": f"Message ID '{message_id}' deleted successfully"
            })
        else:
            await self.send_json({
                "error": "Failed to delete message. It may not exist or you are not the sender."
            })

    # ---------------------------
    # Edit Message
    # ---------------------------
    async def edit_message(self, content):
        message_id = content.get("message_id")
        new_content = content.get("new_content", "").strip()
        if not message_id or not new_content:
            await self.send_json({"error": "message_id and new_content are required"})
            return

        @database_sync_to_async
        def edit_message_in_db():
            try:
                message = Message.objects.get(id=message_id, group__name=self.group_name)
                if message.sender != self.user:
                    return False  # Only sender can edit their message
                message.content = new_content
                message.save()
                return True
            except Message.DoesNotExist:
                return False

        success = await edit_message_in_db()
        if success:
            await self.send_json({
                "message": f"Message ID '{message_id}' edited successfully"
            })
        else:
            await self.send_json({
                "error": "Failed to edit message. It may not exist or you are not the sender."
            })

    # ---------------------------
    # Reply to Message
    # ---------------------------
    async def reply_message(self, content):
        original_message_id = content.get("reply_to")  # original message id
        reply_content = content.get("reply_content", "").strip()
        if not original_message_id or not reply_content:
            await self.send_json({"error": "original_message_id and reply_content are required"})
            return

        @database_sync_to_async
        def reply_to_message_in_db():
            try:
                original_message = Message.objects.get(id=original_message_id, group__name=self.group_name)
                reply_message = Message.objects.create(
                    sender=self.user,
                    content=reply_content,
                    group=original_message.group,
                    #reply_to=original_message
                )
                return reply_message
            except Message.DoesNotExist:
                return None

        reply_message = await reply_to_message_in_db()
        if reply_message:
            await self.send_json({
                "message": f"Replied to message ID '{original_message_id}' successfully",
                "reply_id": reply_message.id
            })
        else:
            await self.send_json({
                "error": "Failed to reply. Original message may not exist."
            })
    
    # ---------------------------
    # Pin Message
    # ---------------------------
    async def pin_message(self, content):
        message_id = content.get("message_id")
        if not message_id:
            await self.send_json({"error": "message_id is required"})
            return

        @database_sync_to_async
        def pin_message_in_db():
            try:
                message = Message.objects.get(id=message_id, group__name=self.group_name)
                message.is_pinned = True
                message.save()
                return True
            except Message.DoesNotExist:
                return False

        success = await pin_message_in_db()
        if success:
            await self.send_json({
                "message": f"Message ID '{message_id}' pinned successfully"
            })
        else:
            await self.send_json({
                "error": "Failed to pin message. It may not exist."
            })
    # Database helpers
    # ---------------------------
    @database_sync_to_async
    def get_or_create_group(self, name, user):
        group, created = Group.objects.get_or_create(
            name=name,
            defaults={"admin": user}
        )
        if created:
            CoAdmin.objects.create(group=group, user=user)
            GroupMembership.objects.create(group=group, user=user)
        return group, created
    # ---------------------------
    # Check if group exists
    # ---------------------------
    @database_sync_to_async
    def group_exists(self, group_name):
        return Group.objects.filter(name=group_name).exists()
    

    @database_sync_to_async
    def add_user_to_group(self, group_name, user):
        try:
            group = Group.objects.get(name=group_name)
            # Check if user is already a member
            if GroupMembership.objects.filter(group=group, user=user).exists():
                return False
            GroupMembership.objects.create(group=group, user=user)
            return True
        except Group.DoesNotExist:
            return False
        

    @database_sync_to_async
    def remove_user_from_group(self, group_name, user):
        try:
            group = Group.objects.get(name=group_name)
            deleted_count, _ = GroupMembership.objects.filter(
                group=group, user=user
            ).delete()
            return deleted_count > 0
        except Group.DoesNotExist:
            return False
        
    @database_sync_to_async
    def save_message_to_db(self, message_text, image_url=None, file_url=None):
      

        try:
            group = Group.objects.get(name=self.group_name)
            msg = Message(
                sender=self.user,
                content=message_text,
                group=group,
                image_url=image_url,  # store the URL directly
                file_url=file_url
            )
            msg.save()
            return msg
        except Group.DoesNotExist:
            return None
        except Exception as e:
            print("Error saving message:", e)
            return None
    # ---------------------------
    # Database-safe message loader
    # ---------------------------
    @database_sync_to_async
    def load_messages_func(self, group_name, limit, offset):
        from chat.models import Group, Message  # ✅ import inside (safer for async)
        try:
            group = Group.objects.get(name=group_name)
            messages = (
                Message.objects.filter(group=group)
                .select_related("sender")  # performance optimization
                .order_by('-timestamp')[offset:offset + limit]
            )
            # Convert queryset to list while still in sync context
            return list(messages)
        except Group.DoesNotExist:
            return []
        
class OneToOneChatConsumer(AsyncJsonWebsocketConsumer):
   
    async def connect(self):
        self.user = self.scope['user']

        if not self.user or self.user.is_anonymous:
              await self.close()
              return
       
        self.friend_username = self.scope["url_route"]["kwargs"]["friend_username"]
        self.friend_user = await self.get_user(self.friend_username)
 
        # Get friend username from URL
        self.friend_username = self.scope["url_route"]["kwargs"].get("friend_username")
        if not self.friend_username:
            await self.close()
            return

        self.friend_user = await self.get_user(self.friend_username)
        if not self.friend_user:
            await self.close()
            return
       # create or get chat
        self.chat = await self.get_or_create_private_chat(self.user, self.friend_user)

        # join the room
        await self.channel_layer.group_add(self.room_name, self.channel_name)
        await self.accept()

        await self.send_json({"status": "connected", "chat_with": self.friend_username})

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_name, self.channel_name)

    
    async def receive_json(self, content):
        action = content.get("action")

        if action == "send_message":
            await self.handle_send_message(content)
        elif action == "load_messages":
            await self.load_messages(content)
        else:
            await self.send_json({"error": "Invalid action"})
 
        
    # -------------------------------
    # Action handlers
    # -------------------------------

    async def handle_send_message(self, content, imaage_url=None, file_url=None):
        message = content.get("message", "").strip()
        image_url = content.get("image_url", "").strip()
        file_url = content.get("file_url", "").strip()

        if not message and not image_url and not file_url:
            await self.send_json({"error": "Message cannot be empty"})
            return

        # Save message to DB
        saved_message = await self.save_message_to_db(message, image_url, file_url)

        # Broadcast to the group
        await self.channel_layer.group_send(
            self.room_name,
            {
                "type": "chat_message",  # triggers chat_message method
                "user": self.user.username,
                "message": message,
                "image_url": image_url,
                "file_url": file_url,
                "timestamp": saved_message.timestamp.isoformat(),
            }
        )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send_json({
            "sender_username": event["user"],
            "message": event["message"],
            "image_url": event["image_url"],
            "file_url": event["file_url"],
            "timestamp": event["timestamp"]
        })


    async def load_messages(self, content):
        limit = int(content.get("limit", 20))
        offset = int(content.get("offset", 0))

        messages = await self.load_messages_func(limit, offset)

        message_list = [
            {
                "id": msg.id,
                "sender": msg.sender.username,
                "content": msg.content,
                "timestamp": timezone.localtime(msg.timestamp).isoformat(),
            }
            for msg in messages
        ]

        await self.send_json({
            "status": "history",
            "count": len(message_list),
            "limit": limit,
            "offset": offset,
            "messages": message_list,
        })


    # Database helpers
    @database_sync_to_async
    def get_user(self, username):
        from django.contrib.auth.models import User
        try:
            return User.objects.get(username=username)
        except User.DoesNotExist:
            return None
        
    @database_sync_to_async
    def get_or_create_private_chat(self, user1, user2):
        chat, created = OneToOneChat.objects.get_or_create(
            user1=min(user1, user2, key=lambda u: u.id),
            user2=max(user1, user2, key=lambda u: u.id)
        )
        self.room_name = f"private_chat_{chat.id}"
        return chat
        
    @database_sync_to_async
    def save_message_to_db(self, message_text):
        try:
            OneToOneChatmassage.objects.create(
                chat = self.chat,
                sender=self.user,
                content=message_text,
                image_url=image_url if image_url else None, 
                file_url=file_url if file_url else None,
               
            )
            return True
        except Exception:
            return False
        
    @database_sync_to_async
    def load_messages_func(self, limit, offset):
        from chat.models import OneToOneChatmassage  # ✅ import inside (safer for async)
        try:
            messages = (
                OneToOneChatmassage.objects.filter(chat=self.chat)
                .select_related("sender")  # performance optimization
                .order_by('-timestamp')[offset:offset + limit]
            )
            # Convert queryset to list while still in sync context
            return list(messages)
        except Exception:
            return []