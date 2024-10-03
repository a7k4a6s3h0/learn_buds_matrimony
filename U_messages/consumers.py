import json
# from asgiref.sync import async_to_sync
# from channels.generic.websocket import WebsocketConsumer

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import ChatRoom ,ChatInfo
from datetime import datetime
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = f"chat_{self.room_name}"

        # Get the username of the connected user
        user = self.scope["user"]

        # Accept WebSocket connection
        await self.accept()

        # Check if the user is authenticated before allowing them to connect
        if user.is_authenticated:
            # Check if the room exists asynchronously
            if await self.room_exists(self.room_name):
                # Fetch the chat room data asynchronously
                chat_room_data = await self.get_chat_room_data(self.room_name)
                print(chat_room_data,"chat datas")

                if user not in chat_room_data.users.all():
                    # Send warning message to the user
                    message = {
                        'type': 'warning',
                        'text': ' you are not a member of this chat..!!!'
                    }

                    # Send message to the client asynchronously
                    await self.send_warning_message(message)
                else:
                    print(user.username, "name")
                    self.username = user.username  # Store the username for later use

                    # Join room group asynchronously
                    await self.channel_layer.group_add(
                        self.room_group_name, self.channel_name
                    )

            else:
                # Send warning message to the user
                message = {
                    'type': 'warning',
                    'text': 'Unauthorized access..!!!'
                }

                # Send message to the client asynchronously
                await self.send_warning_message(message)
        else:
            print("User is not authenticated")
            message = {
                'type': 'warning',
                'text': 'Authentication required.'
            }

            # Send message to the client asynchronously
            await self.send_warning_message(message)

    @database_sync_to_async
    def room_exists(self, room_name):
        return ChatRoom.objects.filter(room_name=room_name).exists()
    
    # Fetch chat room data from the database
    @database_sync_to_async
    def get_chat_room_data(self, room_name):
        try:
            return ChatRoom.objects.get(room_name=room_name)
        except ChatRoom.DoesNotExist:
            return None

    # Send warning message to WebSocket
    async def send_warning_message(self, message):
        warning_message = message['text']
        await self.send(text_data=json.dumps({"Warning_Message": warning_message}))
        # Disconnect the user after sending the warning
        await self.close(code=4001)

    async def disconnect(self, close_code):
        # Leave room group asynchronously
        await self.channel_layer.group_discard(
            self.room_group_name, self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group asynchronously
        print(message, "from web")

        data_set = {
            "type": "chat_message",
            "username": self.username,
            'isSender': True,
            "message": message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # Include current timestamp
        }

        await self.channel_layer.group_send(
            self.room_group_name, data_set
        )

    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket asynchronously
        await self.send(text_data=json.dumps(event))


    
