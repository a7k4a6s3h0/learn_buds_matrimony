from collections.abc import Iterable
from django.db import models
from U_auth.models import *
import uuid
# Create your models here.

class ChatRoom(models.Model):

     ROOM_TYPE = [
          ('normal', 'normal'),
          ('group', 'group')
     ]

     room_name = models.CharField(max_length=255, blank=True)
     room_type = models.CharField(choices=ROOM_TYPE,max_length=255)
     users = models.ManyToManyField(costume_user)

     def save(self, *args, **kwargs):
        # Check if room_name is empty
        if not self.room_name:
            # Generate a random room name (similar to '66f116ed-c50c')
            self.room_name = f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:4]}"
        
        super().save(*args, **kwargs)
     

class ChatInfo(models.Model):

     USER_TYPES = [
          ('sender', 'sender'),
          ('reciever', 'reciever'),
     ]
     
     chat_name = models.ForeignKey(ChatRoom,  on_delete=models.CASCADE,  related_name='chatroom_data')
     messages = models.CharField(max_length=255)
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)
     sender = models.ForeignKey(costume_user, on_delete=models.CASCADE,  related_name='chat_senderinfo')
     # user_type = models.CharField(choices=USER_TYPES, max_length=20)
     receiver = models.ForeignKey(costume_user, on_delete=models.CASCADE,  related_name='chat_receiverinfo')
     class Meta:
          verbose_name = "ChatInfo"
          verbose_name_plural = "ChatInfos"

     def __str__(self):
          return self.chat_name.room_type


class NotificationRoom(models.Model):

     room_name = models.CharField(max_length=255, blank=True)
     user = models.ForeignKey(costume_user, related_name='notification_user_room', on_delete=models.CASCADE)
     created_at = models.DateTimeField(auto_now_add=True)

     def save(self, *args, **kwargs):
        # Check if room_name is empty
        if not self.room_name:
            # Generate a random room name (similar to '66f116ed-c50c')
            self.room_name = f"{uuid.uuid4().hex[:8]}-{uuid.uuid4().hex[:4]}"
        
        super().save(*args, **kwargs)


class NotificationDetails(models.Model):

     SEND_VIA = [
          ('email', 'email'),
          ('sms', 'sms'),
          ('inapp',  'inapp')
     
     ]

     AIMED_AUDIENCES = [
         ('id',  'id'),
         ('selected', 'selected'),
         ('location',  'location'),
     ]

     TARGETED_MODULE = [
         ('matrimony',  'matrimony'),
         ('job-portal', 'job-portal'),
         ('dating', 'dating'),
         ('ecommerce', 'ecommerce'),
         ('study-aboard', 'study-aboard'),
     ]

     user = models.ForeignKey(costume_user, related_name='notification_user', on_delete=models.CASCADE)
     title = models.CharField(max_length=50)
     description = models.CharField(max_length=250)
     image = models.ImageField(upload_to='notification-images/', null=True, blank=True)
     targeted_audiences = models.CharField(choices=AIMED_AUDIENCES, max_length=20)
     target_specific = models.CharField(choices=TARGETED_MODULE, max_length=15)
     other_service = models.CharField(choices=SEND_VIA, max_length=15)
     start_at = models.DateField()
     end_at = models.DateField()
     created_at = models.DateTimeField(auto_now_add=True)
     updated_at = models.DateTimeField(auto_now=True)
     is_read = models.BooleanField(default=False)

     def __str__(self):
         return f"notification_{self.title}"
     


class AmidUsers(models.Model):
    notification_obj = models.ForeignKey(NotificationDetails,  related_name='amid_users', on_delete=models.CASCADE)
    users = models.ManyToManyField(costume_user, blank=True)
    locations = models.ManyToManyField(UserPersonalDetails,blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self) -> str:
        return f"targetuser_{self.notification_obj.title}"