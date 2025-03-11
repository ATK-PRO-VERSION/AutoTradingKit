
import asyncio
from fastapi import WebSocket, WebSocketDisconnect
from typing import List, Dict

from ..controls.models import *
from .ta_indicators import *
from .ta_indicators import IndicatorType
  
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[:str:List[WebSocket]] = {}

    def get_sockets(self):
        return list(self.active_connections.keys())
    
    def get_socket_by_name(self,socket_infor):
        chart_id = socket_infor.get("chart_id")
        id_exchange = socket_infor.get("id_exchange")
        symbol:str=socket_infor.get("symbol")
        interval:str=socket_infor.get("interval")
        socket_name = f"{chart_id}-{id_exchange}-{symbol}-{interval}"
        return  self.active_connections.get(socket_name)

    
    async def connect(self, socket_infor,websocket: WebSocket):
        chart_id = socket_infor.get("chart_id")
        id_exchange = socket_infor.get("id_exchange")
        symbol:str=socket_infor.get("symbol")
        interval:str=socket_infor.get("interval")
        socket_name = f"{chart_id}-{id_exchange}-{symbol}-{interval}"
        if self.socket_is_active(websocket):
            await self.disconnect(socket_infor,websocket)
        self.active_connections[socket_name]=websocket

    async def disconnect(self,socket_infor, websocket: WebSocket):
        print(f"{websocket} is closed")
        chart_id = socket_infor.get("chart_id")
        id_exchange = socket_infor.get("id_exchange")
        symbol:str=socket_infor.get("symbol")
        interval:str=socket_infor.get("interval")
        socket_name = f"{chart_id}-{id_exchange}-{symbol}-{interval}"
        sk = self.active_connections.get(socket_name)
        if sk:
            del self.active_connections[socket_name]
            await websocket.close()

    def socket_is_active(self,websocket: WebSocket):
        if websocket in self.active_connections.values():
            return True
        return False

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections.values():
            await connection.send_text(message)
            