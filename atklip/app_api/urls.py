from .var import host,port
socket_url = "ws://127.0.0.1:2022/indicator"


class ApiURL:
    def __init__(self):
        self.host = host
        self.port = port
        self.url_test = f"http://{self.host}:{self.port}/test"
        self.url_active_candles = f"http://{self.host}:{self.port}/get-active-candles"

        self.url_add_smooth_candle = f"http://{self.host}:{self.port}/add-smooth-candle"
        self.url_change_smooth_candle = f"http://{self.host}:{self.port}/change-smooth-candle-input"
        self.url_delete_smooth_candle = f"http://{self.host}:{self.port}/delete-smooth-candle"
        
        self.url_add_indicator = f"http://{self.host}:{self.port}/add-indicator"
        self.url_change_indicator_input = f"http://{self.host}:{self.port}/change-indicator-input"
        self.url_delete_indicator = f"http://{self.host}:{self.port}/delete-indicator"
        
        self.url_load_historic = f"http://{self.host}:{self.port}/load-historic-data"
        self.url_reset_chart = f"http://{self.host}:{self.port}/reset-chart"
        self.url_goto_date = f"http://{self.host}:{self.port}/goto-date"
        self.url_get_active_indicator = f"http://{self.host}:{self.port}/get-active-indicators"
                

        self.ws_setup_market = f"ws://{self.host}:{self.port}/create-market"
        self.ws_change_market = f"ws://{self.host}:{self.port}/change-market"
        self.ws_reconnect_market = f"ws://{self.host}:{self.port}/re-connect-market"
             

    def url_get_candle_data(self,start:int=0,stop:int=0):
        return f"http://{self.host}:{self.port}/get-candle-data/?start={start}&stop={stop}"
    
    def url_get_volume_data(self,start:int=0,stop:int=0):
        return f"http://{self.host}:{self.port}/get-volume-data/?start={start}&stop={stop}"
    
    def url_get_indicator_data(self,start:int=0,stop:int=0):
        return f"http://{self.host}:{self.port}/get-indicator-data/?start={start}&stop={stop}"