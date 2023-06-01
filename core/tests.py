import json

import websocket


def on_open(ws):
    print("WebSocket connection opened")
    ws.send(json.dumps({'message': "CHECK"}))


def on_message(ws, message):
    message = eval(message)
    if message.get('body') == "CHECK":
        ws.close()
    print(f"Received message: {message}")


def on_error(ws, error):
    print(f"Error: {error}")


def on_close(ws):
    print("WebSocket connection closed")


ws = websocket.WebSocketApp(
    'ws://127.0.0.1:8000/ws/socket-server/?group_name=15100',
    on_message=on_message,
    on_error=on_error,
    on_close=on_close,
    on_open=on_open,
)
ws.run_forever()
