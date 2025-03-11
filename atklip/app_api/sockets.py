import asyncio
# import tracemalloc
import gc
from typing import List
from fastapi import FastAPI, Request, WebSocketDisconnect
from ccxt import NetworkError
from fastapi import FastAPI, WebSocket
from ..controls.models import *
from .ta_indicators import *
from .indicatormanager import IndicatorManager

from slowapi import Limiter
from slowapi.util import get_remote_address

app = FastAPI()
# Tạo limiter với giới hạn cụ thể
limiter = Limiter(key_func=get_remote_address)
gc.set_threshold(700, 10, 10)

# tracemalloc.start()

managerindicator = IndicatorManager()

@app.get("/test")
async def test():
    return  {"alive": True}

# Endpoint để xem tình trạng bộ nhớ hiện tại
# @app.get("/memory-stats")
# def memory_stats():
#     # Lấy bức ảnh bộ nhớ hiện tại
#     snapshot = tracemalloc.take_snapshot()
#     top_stats = snapshot.statistics('lineno')

#     # Hiển thị top 10 vùng bộ nhớ đang sử dụng nhiều nhất
#     memory_details = []
#     for stat in top_stats[:20]:
#         memory_details.append({
#             "file": stat.traceback[0].filename,
#             "line_no": stat.traceback[0].lineno,
#             "size": stat.size / 1024,  # Chuyển đổi sang KB
#             "count": stat.count
#         })

#     return {"memory_stats": memory_details}

# Endpoint để reset tracemalloc (xóa các snapshot hiện tại)
# @app.get("/reset-tracemalloc")
# def reset_tracemalloc():
#     tracemalloc.clear_traces()
#     return {"message": "Tracemalloc has been reset."}

@app.get("/get-candle-data/")
@limiter.limit("5000000/minute")
async def get_index_data(start:int,stop:int,request: Request):
    candle_infor = await request.json()
    # print(candle_infor)
    candle,source_name = managerindicator.get_candle(candle_infor)
    if candle != None:
        return candle.get_index_data(start=start,stop=stop)
    else:
        return {}
    
@app.get("/get-volume-data/")
@limiter.limit("5000000/minute")
async def get_index_volumes(start:int,stop:int,request: Request):
    candle_infor = await request.json()
    candle,source_name = managerindicator.get_candle(candle_infor)
    # print(candle_infor,candle)
    if candle != None:
        return candle.get_index_volumes(start=start,stop=stop)
    else:
        return {}

@app.get("/load-historic-data/")
@limiter.limit("5000000/minute")
async def load_historic_data(request: Request):
    candle_infor = await request.json()
    output = managerindicator.load_historic_data(candle_infor)
    return output


@app.get("/reset-chart/")
@limiter.limit("5000000/minute")
async def reset_chart(request: Request):
    candle_infor = await request.json()
    output = managerindicator.reset_data(candle_infor)
    return output

@app.get("/goto-date/")
@limiter.limit("5000000/minute")
async def goto_date(request: Request):
    """_summary_
    Args:
        gototime (int): _description_
        request (Request): _description_
    Returns:
        _type_: _description_
    """
    candle_infor = await request.json()
    output = managerindicator.goto_date(candle_infor)
    return output

@app.get("/add-smooth-candle")
@limiter.limit("5000000/minute")
async def add_smooth_candle(request: Request):
    """_summary_
        mamode:requied for both (smoothcandle or supersmoothcandle)
        ma_leng:requied for both (smoothcandle or supersmoothcandle)
        n_smooth:requied for only supersmoothcandle
        name: smoothcandle or supersmoothcandle
        source:japan or heikinashi
        precision:requied
    Args:
        request (Request): _description_
    """
    candle_infor = await request.json()
    candle = managerindicator.add_candle(candle_infor)
    candle.fisrt_gen_data()
    return {"result": "Done"}

@app.get("/add-indicator")
@limiter.limit("5000000/minute")
async def add_indicator(request: Request):
    """_summary_
        ta_infor : {
            ta_param: indicator.name = ta_param
            source_name: candle.source_name
        }
    Args:
        request (Request): _description_
    """
    infor = await request.json()
    # print(infor)
    list_done=[]
    list_ta_infors = infor["list_ta"]
    if list_ta_infors != []:
        for ta_infor in list_ta_infors:
            indicator = managerindicator.add_indicator(ta_infor)
            if indicator == None:
                list_done.append({f"Indicator is not supported ":ta_infor})
                continue
            list_done.append({indicator.name: f"{indicator.name} has been added"})  
    return  {"result": list_done}

@app.get("/get-indicator-data/")
@limiter.limit("5000000/minute")
async def get_indicator_data(start:int,stop:int,request: Request):
    """_summary_
        obj_id: obj_id
    Args:
        request (Request): start and stop index
    """
    ta_infor = await request.json()
    indicator = managerindicator.get_indicator(ta_infor)
    if indicator != None:
        return indicator.get_data(start=start,stop=stop)
    return {}

@app.get("/change-indicator-input/")
@limiter.limit("5000000/minute")
async def change_indicator_input(request: Request):
    """_summary_
        ta_infor: {"obj_id":"fdsfdfdsf",
                "source_name":"this_is_my_fastapi-smooth_exam-binanceusdm-japan-smoothcandle-ETHUSDT-3m-ema-3",
                "legs":3,
                "deviation":1}
    """
    ta_infor = await request.json()
    output = managerindicator.change_input_indicator(ta_infor)
    return output

@app.get("/delete-indicator/")
@limiter.limit("5000000/minute")
async def delete_indicator(request: Request):
    """_summary_
        ta_infor: [{"obj_id":"fdsfdfdsf"},...]
    """
    list_indicators = await request.json()
    list_ta_infor = list_indicators.get("list_indicators",[])
    output:list = []
    if list_indicators != []:
        for ta_infor in list_ta_infor:
            detail = managerindicator.delete_indicator(ta_infor)
            output.append(detail)
    return output


@app.get("/get-active-market/")
async def active_markets():
    """_summary_

    Returns:
        _type_: _description_
    """
    active_market = managerindicator.mnsocket.get_sockets()
    return {"markets":active_market}

@app.get("/get-active-candles/")
@limiter.limit("5000000/minute")
async def active_candles(request: Request):
    """_summary_
    Returns:
        _type_: _description_
    """
    candle_infor = await request.json()
    active_candle = managerindicator.get_all_candles_on_chart(candle_infor)
    return {"candles":active_candle}

@app.get("/get-active-indicators/")
async def active_indicators():
    """_summary_
    Returns:
        _type_: _description_
    """
    indicators = managerindicator.get_all_candles_on_chart()
    return indicators

@app.get("/change-smooth-candle-input")
@limiter.limit("5000000/minute")
async def change_smooth_candle_input(request: Request):
    """_summary_
    Change input of smooth and super smooth candle
    Returns:
        candle_infor: old and new candle_infor: this function only for smooth and super-smooth-candle
    """
    candle_infor = await request.json()
    
    old_candle_infor = candle_infor["old"]
    new_candle_infor  = candle_infor["new"]
    
    candle:SMOOTH_CANDLE|N_SMOOTH_CANDLE
    candle,old_source_name = managerindicator.get_candle(old_candle_infor)
    
    name:str=new_candle_infor.get("name")
    
    if candle == None:
        return  {"result": f"{name} is not exist"}
    if name == "smoothcandle":
        candle.change_input(None,new_candle_infor)
    elif name == "japancandle":
        return {"result": "Japancandle is not supported to change input"}
    elif name == "supersmoothcandle":
        candle.change_input(None,new_candle_infor)
    elif name == "heikinashi":
        return {"result": "Heikinashi is not supported to change input"}
    
    if old_source_name in list(managerindicator.map_candle.keys()):
        managerindicator.map_candle[candle.source_name] = managerindicator.map_candle.pop(old_source_name)
    else:
        managerindicator.map_candle[candle.source_name] = candle
    output_data = {}
    output_data.update({candle.source_name: candle.get_index_data()})
    "change input indicator"
    list_indicator = managerindicator.get_list_indicator_of_candle(candle)
    if list_indicator != []:
        for indicator in list_indicator:
            indicator.change_input(candles=candle)
            while True:
                if indicator.is_current_update == True:
                    output_data.update({indicator.name: indicator.get_data()})
                    indicator.is_current_update = False
                    break
           
    return output_data


@app.websocket("/create-market")
async def create_market(websocket: WebSocket):
    """_summary_
    ham nay de genarate new candle
    Args:
        websocket (WebSocket): _description_
    """
    await websocket.accept()
    socket_infor = await websocket.receive_json()
    await managerindicator.mnsocket.connect(socket_infor,websocket)
    id_exchange = socket_infor.get("id_exchange")
    chart_id = socket_infor.get("chart_id")
    client_exchange,ws_exchange= managerindicator.mnexchange.add_exchange(id_exchange,chart_id)
   
    client_exchange.load_markets()
    await ws_exchange.load_markets()
    
    reload_markets = asyncio.create_task(managerindicator.mnexchange.reload_markets(client_exchange,ws_exchange,websocket))
    
    jp_candle,heikin_candle,symbol,interval,_precision = managerindicator.setup_market(client_exchange,socket_infor)
    try:
        await managerindicator.loop_watch_ohlcv(websocket,ws_exchange,client_exchange,jp_candle,heikin_candle,id_exchange,symbol,interval,_precision)
    except (WebSocketDisconnect,NetworkError):
        await managerindicator.mnsocket.disconnect(socket_infor,websocket)
    finally:
        "remove old exchange"
        old_id_exchange = socket_infor.get("id_exchange")
        await managerindicator.mnexchange.remove_exchange(old_id_exchange,chart_id)
        reload_markets.cancel()

@app.websocket("/re-connect-market")
async def re_connect_market(websocket: WebSocket):
    """_summary_
    ham nay de genarate new candle
    Args:
        websocket (WebSocket): _description_
    """
    await websocket.accept()
    socket_infor = await websocket.receive_json()
    await managerindicator.mnsocket.connect(socket_infor,websocket)
    id_exchange = socket_infor.get("id_exchange")
    chart_id = socket_infor.get("chart_id")
    client_exchange,ws_exchange= managerindicator.mnexchange.add_exchange(id_exchange,chart_id)
   
    client_exchange.load_markets()
    await ws_exchange.load_markets()
    
    reload_markets = asyncio.create_task(managerindicator.mnexchange.reload_markets(client_exchange,ws_exchange,websocket))
    
    jp_candle,heikin_candle,symbol,interval,_precision = managerindicator.re_connect_market(client_exchange,socket_infor)
    if jp_candle == None:
        "remove old exchange"
        old_id_exchange = socket_infor.get("id_exchange")
        await managerindicator.mnexchange.remove_exchange(old_id_exchange,chart_id)
        reload_markets.cancel()
    else:
        try:
            await managerindicator.loop_watch_ohlcv(websocket,ws_exchange,client_exchange,jp_candle,heikin_candle,id_exchange,symbol,interval,_precision)
        except (WebSocketDisconnect,NetworkError):
            await managerindicator.mnsocket.disconnect(socket_infor,websocket)
        finally:
            "remove old exchange"
            old_id_exchange = socket_infor.get("id_exchange")
            await managerindicator.mnexchange.remove_exchange(old_id_exchange,chart_id)
            reload_markets.cancel()

@app.get("/delete-smooth-candle/")
@limiter.limit("5000000/minute")
async def delete_smooth_candle(request: Request):
    """_summary_
        {"chart_id": "this_is_my_fastapi",
        "canlde_id":"super_smooth_exam",
        "id_exchange":"binanceusdm",
        "symbol":"ETHUSDT",
        "interval":"3m",
        "mamode":"ema",
        "ma_leng":3,
        "n_smooth":13,
        "name":"supersmoothcandle",
        "source":"japan",
        "precision":3}
    """
    candle_infor = await request.json()
    output = managerindicator.delete_smooth_candle(candle_infor)
    return output


@app.websocket("/change-market")
async def change_market(websocket: WebSocket):
    """_summary_
    ham nay de genarate new candle
    Args:
        websocket (WebSocket): _description_
    """   
    await websocket.accept()
    socket_infor = await websocket.receive_json()
    old_socket_infor = socket_infor["old"]
    new_socket_infor  = socket_infor["new"]
    await managerindicator.mnsocket.connect(new_socket_infor,websocket)
    
    "check old socket and disconnect its"
    old_socket = managerindicator.mnsocket.get_socket_by_name(old_socket_infor)
    if old_socket != None:
        await managerindicator.mnsocket.disconnect(old_socket_infor,old_socket)
    "add and setup new-exchange"
    new_chart_id = new_socket_infor.get("chart_id")
    new_id_exchange = new_socket_infor.get("id_exchange")
    
    client_exchange,ws_exchange= managerindicator.mnexchange.add_exchange(new_id_exchange,new_chart_id)
    
    if client_exchange == None  or ws_exchange==None:
        client_exchange,ws_exchange= managerindicator.mnexchange.add_exchange(new_id_exchange,new_chart_id)
    try:
        client_exchange.load_markets()
        await ws_exchange.load_markets()
    except:
        try:
            client_exchange,ws_exchange= managerindicator.mnexchange.add_exchange(new_id_exchange,new_chart_id)
            client_exchange.load_markets()
            await ws_exchange.load_markets()
        except:
            await websocket.send_json({"error": "can't load markets"})
            await websocket.close()
            return
    reload_markets = asyncio.create_task(managerindicator.mnexchange.reload_markets(client_exchange,ws_exchange,websocket))
    
    try:
        jp_candle, heikin_candle,new_symbol,new_interval, _precision = managerindicator.reset_candle(client_exchange,old_socket_infor,new_socket_infor)    
        
        if jp_candle == None:
            jp_candle,heikin_candle,new_symbol,new_interval,_precision = managerindicator.setup_market(client_exchange,new_socket_infor)
    except Exception as e:
        print(e) 
        jp_candle,heikin_candle,new_symbol,new_interval,_precision = managerindicator.setup_market(client_exchange,new_socket_infor)
    
    if jp_candle == None:
        websocket.send_json({"detail":"Can not connect to exchange, please check internet connection!"}) 
        return
    
    try:
        await managerindicator.loop_watch_ohlcv(websocket,ws_exchange,client_exchange,jp_candle,heikin_candle,new_id_exchange,new_symbol,new_interval,_precision)
    except (WebSocketDisconnect,NetworkError):
        await managerindicator.mnsocket.disconnect(new_socket_infor,websocket)
    finally:
        new_id_exchange = new_socket_infor.get("id_exchange")
        chart_id = new_socket_infor.get("chart_id")
        await managerindicator.mnexchange.remove_exchange(new_id_exchange,chart_id)
        reload_markets.cancel()