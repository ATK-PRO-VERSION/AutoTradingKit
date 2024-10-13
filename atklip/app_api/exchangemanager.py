import asyncio
from typing import Any, Dict
from ccxt import RequestTimeout
from ..controls.models import *
from .ta_indicators import *
from .ta_indicators import CryptoExchange,CryptoExchange_WS



class ExchangeManager:
    def __init__(self) -> None:
        self.map_exchange:Dict[str:any] = {}
        self.map_chart_exchange:Dict[str:dict] = {}

    def add_exchange(self,id_exchange,chart_id):
        client = self.set_client_exchange(id_exchange,chart_id)
        ws = self.set_ws_exchange(id_exchange,chart_id)
        return client,ws
    
    def set_ws_exchange(self,id_exchange,chart_id):
        ws = CryptoExchange_WS().setupEchange(exchange_name=id_exchange)
        chart = self.map_chart_exchange.get(chart_id)
        if chart == None:
            self.map_chart_exchange[chart_id] = {f"ws-{id_exchange}":ws}
        else:
            self.map_chart_exchange[chart_id].update({f"ws-{id_exchange}":ws})
        return ws

    def set_client_exchange(self,id_exchange,chart_id):
        client = CryptoExchange().setupEchange(exchange_name=id_exchange)
        chart = self.map_chart_exchange.get(chart_id)
        if chart==None:
            self.map_chart_exchange[chart_id] = {f"client-{id_exchange}":client}
        else:
            self.map_chart_exchange[chart_id].update({f"client-{id_exchange}":client})
        return client
    
    def get_ws_exchange(self,id_exchange,chart_id):
        chart = self.map_chart_exchange.get(chart_id)
        if chart !=None:
            return chart.get(f"ws-{id_exchange}")
        return chart
        

    def get_client_exchange(self,id_exchange,chart_id):
        chart = self.map_chart_exchange.get(chart_id)
        if chart !=None:
            return chart.get(f"client-{id_exchange}")
        return chart
    
    
    async def reload_markets(self,client_socket,ws_socket,websocket):
        n=0
        while True:
            try:
                await asyncio.sleep(10)
                await websocket.send_text("ping")
                pong = await websocket.receive_text()
                if pong == "pong":
                    print(pong)
                n+=1
                if n == 6:
                    ws_market = await ws_socket.load_markets(True)
                    client_market = client_socket.load_markets(True)
                    print(f'{client_socket} --- Markets reloaded')
                    n=0
            except RequestTimeout:
                ws_market = await ws_socket.load_markets()
                client_market = client_socket.load_markets()
                print(f'{client_socket} --- Markets reloaded')
            except Exception as e:
                print(type(e).__name__, str(e))
                # break
    
    async def remove_exchange(self,id_exchange:str,chart_id):
        try:
            ws = self.get_ws_exchange(id_exchange,chart_id)
            if ws:
                await ws.close()
            cl = self.get_client_exchange(id_exchange,chart_id)
            if ws:
                cl.close()
            self.map_chart_exchange[chart_id] == {}
        except:
            pass
        