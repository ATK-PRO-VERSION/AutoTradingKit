from psygnal import evented
from dataclasses import dataclass

#@evented
@dataclass
class Object:
    id: str

@dataclass
class BaseCandleModel():
    chart_id: str
    canlde_id:str
    name:str
    id_exchange:str
    symbol:str
    interval:str
#@evented
@dataclass
class SmoothCandleModel(BaseCandleModel):
    ma_type:str
    ma_leng:int
    source:str
    precision:float
#@evented
@dataclass
class SuperSmoothCandleModel(BaseCandleModel):
    ma_type:str
    ma_leng:int
    n_smooth:int
    source:str
    precision:float
#@evented

@dataclass
class IndicatorBase:
    obj_id:str
    ta_name:str
    source_name:str


@dataclass
class ZigzagModel(IndicatorBase):
    legs:int
    devision:float
    precision:float
#@evented
@dataclass
class MACDModel(IndicatorBase):
    source:str 
    slow_period:int 
    fast_period:int
    signal_period:int
    ma_type: str 
#@evented
@dataclass
class MAModel(IndicatorBase):
    ma_type:str 
    source:str 
    length:int
#@evented
@dataclass
class BBandsModel(IndicatorBase):
    ma_type:str 
    source:str 
    length:int 
    std_dev_mult:float 
#@evented
@dataclass         
class DonchainModel(IndicatorBase):
    lower_length:int 
    upper_length:int 
#@evented
@dataclass 
class ROCModel(IndicatorBase):
    source:str    
    length:int
#@evented
@dataclass
class ROCModel(IndicatorBase):
    source:str    
    length:int 
    ma_type:str 
#@evented
@dataclass
class RSIModel(IndicatorBase):
    source:str    
    length:int 
    ma_type:str 
#@evented
@dataclass    
class STCModel(IndicatorBase):
    source:str   
    tclength:int
    fast:int 
    slow:int 
    ma_type:str 
#@evented
@dataclass
class STOCHModel(IndicatorBase):
    smooth_k_period:int 
    k_period:int 
    d_period:int 
    ma_type:str 
#@evented
@dataclass
class STOCHRSIModel(IndicatorBase):
    rsi_period:int 
    period:int
    k_period:int
    d_period:int 
    source:str 
    ma_type:str 
#@evented
@dataclass 
class VORTEXModel(IndicatorBase):
    period :int
    drift :int
#@evented
@dataclass
class TRIXModel(IndicatorBase):
    length_period :int 
    signal_period:int 
    source:str 
    ma_type:str
#@evented
@dataclass          
class TSIModel(IndicatorBase):
    fast_period :int 
    slow_period :int 
    signal_period:int 
    source:str 
    ma_type:str 
#@evented
@dataclass
class UOModel(IndicatorBase):
    fast_period :int
    medium_period :int
    slow_period :int
    fast_w_value :float
    medium_w_value :float
    slow_w_value :float
    drift  :int
    offset :int
