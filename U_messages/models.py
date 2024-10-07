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



