import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer


class NotificationConsumer(WebsocketConsumer):

    def connect(self):
        group_name = self.scope['query_string'].decode('utf-8')
        group_name = str(group_name).replace('group_name=', '')
        self.room_group_name = group_name
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()
        print("Connection accepted")
        self.send(text_data=json.dumps({
            'type': 'message',
            'message': "CONNECTION ESTABLISHED WITH NEW SOCKET"
        }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        try:
            message = text_data_json['message']
            print(f"Message: {message}")
            async_to_sync(self.channel_layer.group_send)(
                self.room_group_name,
                {
                    'type': 'send_message',
                    'message': message
                }
            )
        except:
            pass

    def send_message(self, event):
        message = event['message']
        try:
            group = event['group']
        except:
            group = "None"
        self.send(text_data=json.dumps({
            'type': 'object',
            'body': message
        }))
        self.send(text_data=json.dumps({
            'type': 'message',
            'body': f'THIS IS DEBUG TEST - {group} - {message}'
        }))
        print("Message Sent")


def send_message_to_group(group_name, message):
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
        group_name,
        {
            'type': 'send_message',
            'message': message,
            'group': group_name

        }
    )
