from django.db import models
from django.contrib.auth import get_user_model
User = get_user_model()

# Create your models here.
class Group(models.Model):
    name= models.CharField(max_length = 255, unique = True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    admin = models.ForeignKey(User, on_delete=models.CASCADE, related_name= 'admin_of_group', null=True, blank=True)

    
    def __str__(self):
        return f"Group: {self.name}, ID: {self.id}"
    

class GroupMembership(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date_joined = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('group', 'user') # একজন ইউজার একই গ্রুপে একাধিকবার থাকতে পারবে না

    def __str__(self):
        return f"{self.user.username} in {self.group.name}"
    
class OneToOneChat(models.Model):
    user1 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user1')
    user2 = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chats_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # নিশ্চিত করে যে দুটি ইউজারের মধ্যে শুধুমাত্র একটি চ্যাট সেশন থাকে
        unique_together = ('user1', 'user2')

    def __str__(self):
        return f"Chat between {self.user1.username} and {self.user2.username}"
    
# মেসেজ মডেল
class Message(models.Model):
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # গ্রুপ চ্যাটের জন্য (optional)
    group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True, blank=True)
    
    # ব্যক্তিগত চ্যাটের জন্য (optional)
    one_to_one_chat = models.ForeignKey(OneToOneChat, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['timestamp'] # মেসেজগুলো সময় অনুযায়ী সাজানো থাকবে

    def __str__(self):
        if self.group:
            return f"Group Message by {self.sender.username} in {self.group.name} at {self.timestamp}"
        elif self.one_to_one_chat:
            return f"One-to-One Message by {self.sender.username} at {self.timestamp}"
        return f"Message by {self.sender.username} at {self.timestamp}"

class CoAdmin(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Co-admin {self.user.username} for {self.group.name}"
    
class OneToOneChatmassage(models.Model):
    chat = models.ForeignKey(OneToOneChat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"One-to-One Message by {self.sender.username} at {self.timestamp}"