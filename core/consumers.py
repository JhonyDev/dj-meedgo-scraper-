import json

from channels.generic.websocket import WebsocketConsumer

from src.api.singletons import ConsumerSingleton


class NotificationConsumer(WebsocketConsumer):
    def connect(self):
        if self.scope.get('is_encoded') is None:
            group_name = self.scope['query_string'].decode('utf-8')
        else:
            group_name = self.scope['query_string']
        group_name = str(group_name).replace('group_name=', '')
        self.room_group_name = group_name
        self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        self.accept()
        print("Connection accepted")
        ConsumerSingleton.set_consumer(self)
        print(self)
        self.send(json.dumps({
            'type': 'message',
            'message': "CONNECTION ESTABLISHED WITH NEW SOCKET"
        }))

    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        try:
            message = text_data_json['message']
            print(f"Message: {message}")
            self.channel_layer.group_send(
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
        self.send(json.dumps({
            'type': 'object',
            'body': message
        }))
        print("Message Sent")


def send_message_to_group(group_name, message):
    # from asgiref.sync import async_to_sync
    # channel_layer = get_channel_layer()
    # async_to_sync(channel_layer.group_send)(
    #     group_name,
    #     {
    #         'type': 'send_message',
    #         'message': message
    #     })
    print(ConsumerSingleton.get_consumer())
    ConsumerSingleton.get_consumer().send(text_data=json.dumps({
        'type': 'message',
        'message': "CHECK FROM SINGLETON"
    }))

    print("MESSAGE SHOULD BE SENT")
