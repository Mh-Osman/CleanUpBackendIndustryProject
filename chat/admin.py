from django.contrib import admin

# Register your models here.
from .models import Group, GroupMembership, OneToOneChat, Message
admin.site.register(Group)
admin.site.register(GroupMembership)    
admin.site.register(OneToOneChat)
admin.site.register(Message)
