import asyncio
from typing import Any, Dict
from ccxt import RequestTimeout
from .models import *
from .ta_indicators import CryptoExchange,CryptoExchange_WS
from qasync import asyncSlot
from atklip.app_utils.syncer import sync

class ExchangeManager:
    def __init__(self) -> None:
        self.map_chart_exchange:Dict[str:dict] = {}
        self.is_stop = False

    def add_exchange(self,id_exchange,chart_id,symbol,interval,apikey,secretkey):
        self.is_stop = False
        client = self.set_client_exchange(id_exchange,chart_id,symbol,interval,apikey,secretkey)
        ws = self.set_ws_exchange(id_exchange,chart_id,symbol,interval,apikey,secretkey)
        print("setupexchange", client, ws)
        return client,ws
    
    def set_ws_exchange(self,id_exchange,chart_id,symbol,interval,apikey,secretkey):
        ws = CryptoExchange_WS().setupEchange(apikey=apikey,secretkey=secretkey,exchange_name=id_exchange)
        chart = self.map_chart_exchange.get(f"ws-{chart_id}-{symbol}-{interval}")
        if chart == None:
            self.map_chart_exchange[f"ws-{chart_id}-{symbol}-{interval}"] = {f"ws-{id_exchange}":ws}
        else:
            self.map_chart_exchange[f"ws-{chart_id}-{symbol}-{interval}"].update({f"ws-{id_exchange}":ws})
        return ws

    def set_client_exchange(self,id_exchange,chart_id,symbol,interval,apikey,secretkey):
        client = CryptoExchange().setupEchange(apikey=apikey,secretkey=secretkey,exchange_name=id_exchange)
        chart = self.map_chart_exchange.get(f"client-{chart_id}-{symbol}-{interval}")
        if chart==None:
            self.map_chart_exchange[f"client-{chart_id}-{symbol}-{interval}"] = {f"client-{id_exchange}":client}
        else:
            self.map_chart_exchange[f"client-{chart_id}-{symbol}-{interval}"].update({f"client-{id_exchange}":client})
        return client
    
    def get_ws_exchange(self,id_exchange,chart_id,symbol,interval):
        chart = self.map_chart_exchange.get(f"ws-{chart_id}-{symbol}-{interval}")
        if chart !=None:
            return chart.get(f"ws-{id_exchange}")
        return chart
        

    def get_client_exchange(self,id_exchange,chart_id,symbol,interval):
        chart = self.map_chart_exchange.get(f"client-{chart_id}-{symbol}-{interval}")
        if chart !=None:
            return chart.get(f"client-{id_exchange}")
        return chart
    
    async def reload_markets(self,id_exchange,chart_id,symbol,interval):
        n=0
        while True:
            try:
                await asyncio.sleep(1)
                n+=1
                client_socket = self.get_client_exchange(id_exchange,chart_id,symbol,interval)
                ws_socket = self.get_ws_exchange(id_exchange,chart_id,symbol,interval)
                if not client_socket or not ws_socket:
                    print("check socket---- ",client_socket,ws_socket)
                    break
                if n==60:
                    n=0
                    client_market = client_socket.load_markets()
                    ws_market = await ws_socket.load_markets()
                    print(f'{id_exchange}-{chart_id}-{symbol}-{interval} --- Markets reloaded')
            except Exception as e:
                print(type(e).__name__, str(e))
                break
        self.is_stop = True

    async def remove_exchange(self,id_exchange:str,chart_id,symbol,interval):
        try:
            ws = self.get_ws_exchange(id_exchange,chart_id,symbol,interval)
            if ws:
                try:
                    await ws.close()
                    del self.map_chart_exchange[f"ws-{chart_id}-{symbol}-{interval}"]
                except: pass
            cl = self.get_client_exchange(id_exchange,chart_id,symbol,interval)
            if ws:
                try:
                    cl.close()  
                    del self.map_chart_exchange[f"client-{chart_id}-{symbol}-{interval}"]
                except: pass
            print("remove all socket--------")
        except:
            pass
    def clear(self):
        self.map_chart_exchange.clear()

