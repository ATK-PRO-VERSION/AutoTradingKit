import asyncio
import json
import time
import websockets


"kiểm tra fastapi có đang chạy không"

import requests

url = "http://127.0.0.1:2022/test"

try:
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        print("FastAPI server is running.")
    else:
        print(f"FastAPI server responded with status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("FastAPI server is not running.")

async def connect_to_websocket():
    n=0
    uri = "ws://127.0.0.1:2022/indicator"  # Địa chỉ WebSocket server FastAPI
    websocket = await websockets.connect(uri)
        # Gửi một tin nhắn tới server
    while True:
        message = {
                    "ta_name": "zigzag",
                    f"data {n}":21312313
                }
        await websocket.send(json.dumps(message))
        print(f"Sent: {message}")

        # Nhận phản hồi từ server
        response = await websocket.recv()
        print(f"Received: {response}")
        time.sleep(0.2)
        n += 1
    else:
        await websocket.close()

# Chạy event loop để kết nối WebSocket
# asyncio.new_event_loop().run_until_complete(connect_to_websocket())
