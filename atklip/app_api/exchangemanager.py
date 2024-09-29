import asyncio
from typing import Any, Dict

from .models import *
from .ta_indicators import *
from .ta_indicators import CryptoExchange,CryptoExchange_WS



class ExchangeManager:
    def __init__(self) -> None:
        self.map_exchange:Dict[str:Any] = {}

    def add_exchange(self,id_exchange):
        self.set_client_exchange(id_exchange)
        self.set_ws_exchange(id_exchange)
    
    def set_ws_exchange(self,id_exchange):
        self.map_exchange[f"ws-{id_exchange}"] = CryptoExchange_WS().setupEchange(exchange_name=id_exchange)
        return self.map_exchange[f"ws-{id_exchange}"]

    def set_client_exchange(self,id_exchange):
        self.map_exchange[f"client-{id_exchange}"] = CryptoExchange().setupEchange(exchange_name=id_exchange)
        return self.map_exchange[f"client-{id_exchange}"]
    
    def get_ws_exchange(self,id_exchange):
        return self.map_exchange[f"ws-{id_exchange}"]

    def get_client_exchange(self,id_exchange):
        return self.map_exchange[f"client-{id_exchange}"]
    
    def remove_exchange(self,id_exchange:str):
        if "ws-" in id_exchange:
            asyncio.run(self.map_exchange[id_exchange].close())
        else:
            self.map_exchange[id_exchange].close()
        del self.map_exchange[id_exchange]