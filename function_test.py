from atklip.app_api import api
from psygnal import Signal



chart_infor = {"chart_id": "this_is_my_fastapi",
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

# chart_infor = {"chart_id": "this_is_my_fastapi",
# "canlde_id":"smooth_exam",
# "id_exchange":"binanceusdm",
# "symbol":"BTCUSDT",
# "interval":"1m",
# "ma_type":"ema",
# "ma_leng":10,
# "name":"smoothcandle",
# "source":"japan",
# "precision":3}

class Signals:
    emit_data = Signal(dict)

def pprint(text):
    print(text)
    
_emit_data = Signals().emit_data
_emit_data.connect(pprint)
"add-smooth-candle"

connector = api.add_smooth_candle(chart_infor)

# connector = api.get_candle_data(chart_infor)
print(connector)
