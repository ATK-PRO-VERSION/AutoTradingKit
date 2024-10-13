import asyncio
from typing import Any, Dict
from atklip.app_utils.syncer import sync

class SocketManager():
    def __init__(self) -> None:
        self.map_socket:Dict[str:Any] = {}
    def add_socket(self,id_socket,socket):
        self.map_socket[id_socket] = socket
    
    def get_socket(self,id_socket):
        return self.map_socket.get(id_socket)
    @sync
    async def delete_socket(self,id_socket):
        if id_socket in list(self.map_socket.keys()):
            await  self.map_socket[id_socket].close()
            del self.map_socket[id_socket]

        