import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.layers import get_channel_layer


class NotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        if self.scope.get('is_encoded') is None:
            group_name = self.scope['query_string'].decode('utf-8')
        else:
            group_name = self.scope['query_string']
        group_name = str(group_name).replace('group_name=', '')
        self.room_group_name = group_name
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print("Connection accepted")
        await self.send(text_data=json.dumps({
            'type': 'message',
            'message': "CONNECTION ESTABLISHED WITH NEW SOCKET"
        }))

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        try:
            message = text_data_json['message']
            print(f"Message: {message}")
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'send_message',
                    'message': message
                }
            )
        except:
            pass

    async def send_message(self, event):
        message = event['message']
        try:
            group = event['group']
        except:
            group = "None"
        await self.send(text_data=json.dumps({
            'type': 'object',
            'body': message
        }))
        print("Message Sent")


def send_message_to_group(group_name, message):
    from asgiref.sync import async_to_sync
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_message',
            'message': message
        })

    print("MESSAGE SHOULD BE SENT")
