import redis.asyncio as redis
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from datetime import datetime

class Send_notification(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        print(self.room_name, "room name")
        self.room_group_name = f"chat_{self.room_name}"

        # Get the username of the connected user
        user = self.scope["user"]
        channel_name = self.channel_name
        print(user, channel_name, "user and channel name")

        # Connect to Redis asynchronously
        redis_client = redis.Redis(host='127.0.0.1', port=6379, db=0)

        # Store channel_name in Redis with user id as the key
        user_key = f"user_{user.id}"
        
        # Check if the user already exists in Redis asynchronously
        if not await redis_client.exists(user_key):  # If user not in Redis, store the channel name
            print(f"User {user.id} not found in Redis, storing channel_name.")
            await redis_client.set(user_key, channel_name)
            print(f"Stored channel_name in Redis: {channel_name}")
        else:
            print(f"User {user.id} already exists in Redis.")
            await redis_client.delete(user_key, channel_name)
            print(f"Deleted channel_name from Redis: {channel_name}")
            await redis_client.set(user_key, channel_name)

        # Add the user to the group for WebSocket communication
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )


        # Accept WebSocket connection
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        data = json.loads(text_data)
        print(data, "data")

        # Use real data or keep 'chat' for testing
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "send_notification",
                "message": json.dumps({  # Send as JSON string
                    "title": "Test Title",  # Replace with dynamic title if needed
                    "description": "Test Description",  # Replace with dynamic description
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "is_read": False,
                    'type_id': True
                })
            }
        )

    async def send_notification(self, event):
        # Send the message to WebSocket
        message = json.loads(event["message"])
        await self.send(text_data=json.dumps({
            "title": message["title"],
            "description": message["description"],
            "timestamp": message["timestamp"],
            "is_read": message["is_read"],
            "type_is": message["type_id"]
     }))
