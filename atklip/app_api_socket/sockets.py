import asyncio
from concurrent.futures import Future
import json
from fastapi import FastAPI, HTTPException,BackgroundTasks
from pydantic import BaseModel

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from typing import Any, List, Dict

from .models import *
from .ta_indicators import *
from .workers import IndicatorWorker


from atklip.app_api_socket.indicators import map_functions
from fastapi.responses import HTMLResponse

app = FastAPI()

class IndicatorManager:
    def __init__(self) -> None:
        self.map_indicator:Dict[str:Any] = {}
    
    def add_indicator(self,indicator):
        self.map_indicator[indicator.name] = indicator

    def remove_indicator(self,indicator):
        if indicator.name in self.map_indicator:
            del self.map_indicator[indicator.name]
    
    
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
        try:
            await websocket.close()
        except:
            pass

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

    
def send_msg(data, websocket:WebSocket):    
    print(data)
    output = {"result": False}
    ta_name = data["ta_name"]
    func = map_functions.get(ta_name,None)
    if func != None:
        if ta_name == "zigzag":
            pass
    asyncio.run(websocket.send_text(json.dumps(output)))


@app.websocket("/indicator")
async def indicator_caculate(websocket: WebSocket,backgroundtask : BackgroundTasks):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            # backgroundtask.add_task(send_msg,data,websocket)
            worker = IndicatorWorker(send_msg,data,websocket)
            worker.start()
    except WebSocketDisconnect:
        await manager.disconnect(websocket)