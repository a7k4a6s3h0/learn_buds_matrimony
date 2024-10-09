from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import NotificationDetails, AmidUsers
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
import redis.asyncio as redis
import json

# Initialize Redis connection (async)
redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)


# Helper function to send notification to a specific user
def send_to_user(user, notification, channel_layer):
    if user:  # Ensure user exists
        user_key = f"user_{user.id}"  # Redis key for user's channel name
        print(f"Checking Redis for user: {user_key}")

        # Retrieve the channel name from Redis asynchronously
        async def get_channel_name():
            return await redis_client.get(user_key)

        # Fetch the channel name (synchronously)
        channel_name = async_to_sync(get_channel_name)()

        if channel_name:
            print(f"Channel name found: {channel_name.decode('utf-8')}")

            # Prepare the message payload
            message = {
                'title': notification.title,
                'description': notification.description,
                'timestamp': notification.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                'is_read': notification.is_read,
                'type_id': False  # Adjust this if necessary
            }

            print(f"Sending message: {message}")

            # Send the message to the WebSocket channel
            async_to_sync(channel_layer.send)(
                channel_name.decode('utf-8'),  # Decode bytes to string
                {
                    'type': 'send_notification',
                    'message': json.dumps(message)
                }
            )
        else:
            print(f"No channel name found for user {user.username}.")
    else:
        print("No user found for the notification.")

@receiver(post_save, sender=AmidUsers)
def send_notification_signal(sender, instance, created, **kwargs):
    # if created:
        channel_layer = get_channel_layer()
        notification = instance.notification_obj

        # Check if the notification is targeted at a specific user
        if notification.targeted_audiences == 'id':
            user = instance.users.first()  # Fetch the first user

            if user and user.is_online:  # Check if user exists and is online
                notification.is_read = True
                notification.save()  # Mark notification as read

            # Send notification to the specific user
            send_to_user(user, notification, channel_layer)

        else:
            print("Targeted audiences not set to 'id', sending to multiple users.")
            user_list = instance.users.all()
            print(user_list,  "User list")
            # Loop through all users in the list and send notification
            for user in user_list:
                print(user.username,  "User")
                send_to_user(user, notification, channel_layer)








# @receiver(post_save, sender=AmidUsers)
# def send_notification_signal(sender, instance, created, **kwargs):
#     if created:
#         channel_layer = get_channel_layer()
#         # Check if the notification is targeted at a specific user
#         if instance.notification_obj.targeted_audiences == 'id':
#             user = instance.users.first()  # Fetch the first user

#             if user and user.is_online:  # Check if user exists and is online
#                 instance.notification_obj.is_read = True
#                 instance.notification_obj.save()  # Mark notification as read

#             is_id = False

#             if user:  # Ensure user exists
#                 print(user.username, "targeted username")
#                 user_key = f"user_{user.id}_channel"  # Redis key for user's channel name
#                 print("Checking Redis for user:", user_key)

#                 # Retrieve the channel name from Redis asynchronously
#                 async def get_channel_name():
#                     return await redis_client.get(user_key)

#                 # Fetch the channel name (synchronously)
#                 channel_name = async_to_sync(get_channel_name)()

#                 if channel_name:
#                     print("Channel name found:", channel_name.decode('utf-8'))

#                     # Prepare the message payload
#                     message = {
#                         'title': instance.notification_obj.title,
#                         'description': instance.notification_obj.description,
#                         'timestamp': instance.notification_obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#                         'is_read': instance.notification_obj.is_read,
#                         'type_id': is_id
#                     }

#                     print(message, 'msg.....>>>!!!')

#                     # Send the message to the WebSocket channel
#                     async_to_sync(channel_layer.send)(
#                         channel_name.decode('utf-8'),  # Decode bytes to string
#                         {
#                             'type': 'send_notification',
#                             'message': json.dumps(message)
#                         }
#                     )
#                 else:
#                     print("No channel name found for the user in Redis.")
#             else:
#                 print("No user found for the notification.")

#         else:
#             print("Targeted audiences not set to 'id'.")


#             user_list = instance.users.all()  # Fetch the first user
#             for user in user_list:
#                 print(user.username, "targeted username")
#                 # if user and user.is_online:  # Check if user exists and is online
#                     # instance.notification_obj.is_read = True
#                     # instance.notification_obj.save()  # Mark notification as read

#                 is_id = False

#                 if user:  # Ensure user exists
#                     # print(user.username, "targeted username")
#                     user_key = f"user_{user.id}_channel"  # Redis key for user's channel name
#                     print("Checking Redis for user:", user_key)

#                     # Retrieve the channel name from Redis asynchronously
#                     async def get_channel_name():
#                         return await redis_client.get(user_key)

#                     # Fetch the channel name (synchronously)
#                     channel_name = async_to_sync(get_channel_name)()

#                     if channel_name:
#                         print("Channel name found:", channel_name.decode('utf-8'))

#                         # Prepare the message payload
#                         message = {
#                             'title': instance.notification_obj.title,
#                             'description': instance.notification_obj.description,
#                             'timestamp': instance.notification_obj.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#                             'is_read': instance.notification_obj.is_read,
#                             'type_id': is_id
#                         }

#                         print(message, 'msg.....>>>!!!')

#                         # Send the message to the WebSocket channel
#                         async_to_sync(channel_layer.send)(
#                             channel_name.decode('utf-8'),  # Decode bytes to string
#                             {
#                                 'type': 'send_notification',
#                                 'message': json.dumps(message)
#                             }
#                         )
#                     else:
#                         print("No channel name found for the user in Redis.")
#                 else:
#                     print("No user found for the notification.")





# @receiver(post_save, sender=NotificationDetails)
# def send_notification_signal(sender, instance, created, **kwargs):
#     print("In signal:", created, instance)
    
#     if not created:  # Only handle updates, not creation
#         print("In signal if")
#         channel_layer = get_channel_layer()

#         # Get the targeted user (assuming there's only one user)
#         targeted_one = AmidUsers.objects.get(notification_obj=instance)
#         if instance.targeted_audiences == 'id':
#             user = targeted_one.users.first()  # Fetch the first user
#             is_id = False
            
#             if user:  # Ensure user exists
#                 print(user.username, "targeted username")
#                 user_key = f"user_{user.id}"  # Redis key for user's channel name
#                 print("Checking Redis for user:", user_key)
                
#                 # Retrieve the channel name from Redis asynchronously
#                 async def get_channel():
#                     return await redis_client.get(user_key)

#                 # Fetch the channel name
#                 channel_name = async_to_sync(get_channel)()
#                 # channel_name = 'specific.c93861f506124caf80fc03914ece1e32ad454ec70e1c4b49a51b6dae1a8c60fc'

#                 if channel_name:
#                     print("Channel name found:", channel_name.decode('utf-8'))

#                     # Prepare the message payload
#                     message = {
#                         'title': instance.title,
#                         'description': instance.description,
#                         'timestamp': instance.created_at.strftime("%Y-%m-%d %H:%M:%S"),
#                         'type_id': is_id
#                     }

#                     print(message, 'msg.....>>>!!!')

#                     # Send the message to the WebSocket channel
#                     async_to_sync(channel_layer.send)(
#                         channel_name.decode('utf-8'),  # Decode bytes to string
#                         {
#                             'type': 'send_notification',
#                             'message': json.dumps(message)
#                         }
#                     )
#                 else:
#                     print("No channel name found for the user in Redis.")
#             else:
#                 print("No user found for the notification.")


#         elif instance.targeted_audiences == 'selected' :
#             users_list = targeted_one.users.all()

#             for user in users_list:
#                 user_key = f"user_{user.id}"  # Redis key for user's channel name



        # elif instance.targeted_audiences == 'matrimony' :
        #     pass


        # elif instance.targeted_audiences == 'location' :
        #     pass

        # # Prepare the message payload
        # message = {
        #     'title': instance.title,
        #     'description': instance.description,
        #     'timestamp': instance.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        #     'type_id': is_id
        # }

        # # Send the message to the WebSocket group
        # async_to_sync(channel_layer.group_send)(
        #     group_name,
        #     {
        #         'type': 'send_notification',
        #         'message': json.dumps(message)
        #     }
        # )
