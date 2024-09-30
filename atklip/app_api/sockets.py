import asyncio
from fastapi import FastAPI, Request, WebSocketDisconnect
from ccxt import NetworkError
from fastapi import FastAPI, WebSocket
from .models import *
from .ta_indicators import *
from .exchangemanager import ExchangeManager
from .indicatormanager import IndicatorManager
from .socketmanager import ConnectionManager

app = FastAPI()

managersocket = ConnectionManager()
managerindicator = IndicatorManager(managersocket)
managerexchange= ExchangeManager()


@app.get("/test")
async def test():
    return  {"result": True}


@app.get("/get-candle-data/")
async def get_index_data(start:int,stop:int,request: Request):
    candle_infor = await request.json()
    print(candle_infor)
    candle = managerindicator.get_candle(candle_infor)
    if candle != None:
        return candle.get_index_data(start=start,stop=stop)
    else:
        return {}
    

@app.get("/get-volume-data/")
async def get_index_volumes(start:int,stop:int,request: Request):
    candle_infor = await request.json()
    candle = managerindicator.get_candle(candle_infor)
    print(candle_infor,candle)
    if candle != None:
        return candle.get_index_volumes(start=start,stop=stop)
    else:
        return {}

@app.get("/add-candle")
async def add_candle(request: Request):
    """_summary_
        ma_type:requied for both (smoothcandle or supersmoothcandle)
        ma_leng:requied for both (smoothcandle or supersmoothcandle)
        n_smooth:requied for only supersmoothcandle
        name: smoothcandle or supersmoothcandle
        source:japan or heikinashi
        precicion:requied
    Args:
        request (Request): _description_
    """
    candle_infor = await request.json()
    candle = managerindicator.add_candle(candle_infor)
    candle.fisrt_gen_data()

@app.get("/add-indicator")
async def add_indicator(request: Request):
    """_summary_
        ta_infor : {
            ta_param: indicator.indicator_name = ta_param
            source_name: candle.source_name
        }
    Args:
        request (Request): _description_
    """
    ta_infor = await request.json()
    managerindicator.add_indicator(ta_infor)

@app.get("/get-indicator-data/")
async def get_indicator_data(start:int,stop:int,request: Request):
    """_summary_
        ta_param: indicator.indicator_name = ta_param
        source_name: candle.source_name
    Args:
        request (Request): _description_
    """
    ta_infor = await request.json()
    indicator = managerindicator.get_indicator(ta_infor)
    if indicator != None:
        return indicator.get_data(start=start,stop=stop)
    return {}

@app.get("/get-active-market/")
async def active_markets():
    """_summary_

    Returns:
        _type_: _description_
    """
    active_market = managersocket.get_sockets()
    return {"markets":active_market}

@app.get("/get-active-candles/")
async def active_candles(request: Request):
    """_summary_
    Returns:
        _type_: _description_
    """
    candle_infor = await request.json()
    active_candle = managerindicator.get_list_candles(candle_infor)
    return {"candles":active_candle}

@app.get("/change-candle-input")
async def change_candle_input(request: Request):
    """_summary_
    Change input candle, then change all indicator, which has source is this candle
    Returns:
        candle_infor: old and new candle_infor: this function only for smooth and super-smooth-candle
    """
    candle_infor = await request.json()
    old_candle_infor = candle_infor["old"]
    new_candle_infor  = candle_infor["new"]
    
    old_candle = managerindicator.get_candle(old_candle_infor)
    
    managerindicator.change_indicator_when_change_candle()
    
    active_candle = managerindicator.get_list_candle()
    return {"candles":active_candle}


@app.websocket("/create-candle")
async def create_candle(websocket: WebSocket):
    """_summary_
    ham nay de genarate new candle
    Args:
        websocket (WebSocket): _description_
    """
    await websocket.accept()
    socket_infor = await websocket.receive_json()
    heartbeat_task = asyncio.create_task(managersocket.send_heartbeat(websocket))
    await managersocket.connect(socket_infor,websocket)
    id_exchange = socket_infor.get("id_exchange")
    managerexchange.add_exchange(id_exchange)
    ws_exchange = managerexchange.get_ws_exchange(id_exchange)
    client_exchange = managerexchange.get_client_exchange(id_exchange)
    
    client_exchange.load_markets()
    await ws_exchange.load_markets()
    
    jp_candle,heikin_candle,symbol,interval,_precision = managerindicator.create_exchange(client_exchange,socket_infor)
    try:
        await managerindicator.loop_watch_ohlcv(websocket,ws_exchange,jp_candle,heikin_candle,symbol,interval,_precision)
    except (WebSocketDisconnect,NetworkError):
        await managersocket.disconnect(socket_infor,websocket)
    finally:
        "remove old exchange"
        old_id_exchange = socket_infor.get("id_exchange")
        await managerexchange.remove_exchange(old_id_exchange)
        heartbeat_task.cancel()

@app.websocket("/change-candle")
async def change_candle(websocket: WebSocket):
    """_summary_
    ham nay de genarate new candle
    Args:
        websocket (WebSocket): _description_
    """   
    await websocket.accept()
    socket_infor = await websocket.receive_json()
    heartbeat_task = asyncio.create_task(managersocket.send_heartbeat(websocket))
    old_socket_infor = socket_infor["old"]
    new_socket_infor  = socket_infor["new"]
    await managersocket.connect(new_socket_infor,websocket)
    
    "check old socket and disconnect its"
    old_socket = managersocket.get_socket_by_name(old_socket_infor)
    if old_socket != None:
        await managersocket.disconnect(old_socket_infor,old_socket)
    # "remove old exchange"
    # old_id_exchange = old_socket_infor.get("id_exchange")
    # await managerexchange.remove_exchange(old_id_exchange)
    
    "add and setup new-exchange"
    new_id_exchange = new_socket_infor.get("id_exchange")
    managerexchange.add_exchange(new_id_exchange)
    
    ws_exchange = managerexchange.get_ws_exchange(new_id_exchange)
    client_exchange = managerexchange.get_client_exchange(new_id_exchange)
    
    client_exchange.load_markets()
    await ws_exchange.load_markets()
    
    
    jp_candle, heikin_candle,new_symbol,new_interval, _precision = managerindicator.reset_candle(client_exchange,old_socket_infor,new_socket_infor)    
    
    # jp_candle,heikin_candle,symbol,interval,_precision = managerindicator.create_exchange(client_exchange,new_socket_infor)
    
    try:
        await managerindicator.loop_watch_ohlcv(websocket,ws_exchange,jp_candle,heikin_candle,new_symbol,new_interval,_precision)
    except (WebSocketDisconnect,NetworkError):
        await managersocket.disconnect(socket_infor,websocket)
    finally:
        old_id_exchange = new_socket_infor.get("id_exchange")
        await managerexchange.remove_exchange(old_id_exchange)
        heartbeat_task.cancel()    
    
