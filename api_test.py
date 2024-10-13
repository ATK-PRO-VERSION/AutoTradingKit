from atklip.app_api import api
from psygnal import Signal


class Signals:
    emit_data = Signal(dict)

def pprint(text):
    print(text)
    
_emit_data = Signals().emit_data
_emit_data.connect(pprint)

chart_infor = {"chart_id": "this_is_my_fastapi",
"id_exchange":"binanceusdm",
"symbol":"BTCUSDT",
"interval":"1m"}
connector = api.connect_to_market(chart_infor,_emit_data)

smooth_infor = {"chart_id": "this_is_my_fastapi",
               "canlde_id":"smooth_exam",
                "id_exchange":"binanceusdm",
                "symbol":"BTCUSDT",
                "interval":"1m",
                "ma_type":"ema",
                "ma_leng":10,
                "n_smooth":13,
                "name":"smoothcandle",
                "source":"japan",
                "precision":3}
smooth = api.add_smooth_candle(smooth_infor)

super_smooth_infor = {"chart_id": "this_is_my_fastapi",
                        "canlde_id":"super_smooth_exam",
                        "id_exchange":"binanceusdm",
                        "symbol":"BTCUSDT",
                        "interval":"1m",
                        "ma_type":"ema",
                        "ma_leng":10,
                        "n_smooth":13,
                        "name":"supersmoothcandle",
                        "source":"japan",
                        "precision":3}
sp_smooth = api.add_smooth_candle(super_smooth_infor)

change_input_smooth_infor = {"old":{"chart_id": "this_is_my_fastapi",
"canlde_id":"smooth_exam",
"id_exchange":"binanceusdm",
"symbol":"ETHUSDT",
"interval":"1m",
"ma_type":"ema",
"ma_leng":3,
"name":"smoothcandle",
"source":"japan",
"precision":3}
,
"new":{"chart_id": "this_is_my_fastapi",
"canlde_id":"smooth_exam",
"id_exchange":"binanceusdm",
"symbol":"ETHUSDT",
"interval":"1m",
"ma_type":"ema",
"ma_leng":9,
"name":"smoothcandle",
"source":"japan",
"precision":3}
}

change_sp_smooth = api.change_input_smooth_candle(change_input_smooth_infor)



