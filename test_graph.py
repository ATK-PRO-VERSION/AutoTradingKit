import asyncio
import json
import random
import time
import websockets


"kiểm tra fastapi có đang chạy không"

import requests

# url = "http://127.0.0.1:2022/test"

# try:
#     response = requests.get(url)
#     print(response)
#     if response.status_code == 200:
#         print("FastAPI server is running.")
#     else:
#         print(f"FastAPI server responded with status code: {response.status_code}")
# except requests.exceptions.ConnectionError:
#     print("FastAPI server is not running.")


import requests
import json

url_data = "http://127.0.0.1:2022/get-candle-data/?start=-1&stop=0"

url_volume = "http://127.0.0.1:2022/get-volume-data/?start=-1&stop=0"


headers = {
  'Content-Type': 'application/json'
}
n=0
def get_data(n):
    candle = random.choice([
        'japancandle',
        'heikinashi',
        'smoothcandle',
        "supersmoothcandle"
    ])
    payload = json.dumps({
                    "id_exchange": "binanceusdm",
                    "symbol": "ETHUSDT",
                    "interval": "1m",
                    "ma_type": "ema",
                    "ma_leng": 3,
                    "n_smooth":13,
                    "name": f"{candle}",
                    "source": "japan",
                    "precision": 3
                    })
    url = random.choice([
        url_data,
        url_volume])
    try:
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        candle = random.choice([
            'japancandle',
            'heikinashi',
            'smoothcandle',
            "supersmoothcandle"
        ])
        payload = json.dumps({
                        "id_exchange": "binanceusdm",
                        "symbol": "ETHUSDT",
                        "interval": "1m",
                        "ma_type": "ema",
                        "ma_leng": 3,
                        "n_smooth":13,
                        "name": f"{candle}",
                        "source": "japan",
                        "precision": 3
                        })
        url = random.choice([
            url_data,
            url_volume])
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        response = requests.request("GET", url, headers=headers, data=payload,timeout=10)
        print(n,response.text)
    except Exception as e:
        print(e)
    n+=1
    return n


async def connect_to_websocket():
    uri = "ws://127.0.0.1:2022/create-market"  # Địa chỉ WebSocket server FastAPI
    websocket = await websockets.connect(uri)
    message = {"id_exchange":"binanceusdm",
                "symbol":"ETHUSDT",
                "interval":"5m",
                "ma_type":"",
                "ma_leng":3,
                "n_smooth":3,
                "name":"japancandle",
                "source":"japan",
                "precision":3}
    await websocket.send(json.dumps(message))
    print(f"Sent: {message}")
        # Gửi một tin nhắn tới server
    # while not websocket.closed:
    # Nhận phản hồi từ server
    try:
        response = await websocket.recv()
        if response != "heartbeat":
            try:
                output= json.loads(response)
                print(output)
            except json.JSONDecodeError:
                print("Invalid JSON response from server.", response)
    except RuntimeError:
        pass
    await websocket.close()

# Chạy event loop để kết nối WebSocket
asyncio.new_event_loop().run_until_complete(connect_to_websocket())
