from dataclasses import dataclass


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

@dataclass
class SmoothCandleModel(BaseCandleModel):
    mamode:str
    ma_leng:int
    source:str
    precision:float

@dataclass
class SuperSmoothCandleModel(BaseCandleModel):
    mamode:str
    ma_leng:int
    n_smooth:int
    source:str
    precision:float


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

@dataclass
class MACDModel(IndicatorBase):
    source:str 
    slow_period:int 
    fast_period:int
    signal_period:int
    mamode: str 


@dataclass
class SQeezeModel(IndicatorBase):
    bb_length:int 
    bb_std:float 
    kc_length:int
    kc_scalar:float
    mom_length:int
    mom_smooth:int
    mamode: str 
    use_tr:bool
    lazybear:bool
    detailed:bool
    


@dataclass
class MAModel(IndicatorBase):
    mamode:str 
    source:str 
    length:int

@dataclass
class VWMAModel(IndicatorBase):
    source:str 
    length:int

@dataclass
class BBandsModel(IndicatorBase):
    mamode:str 
    source:str 
    length:int 
    std_dev_mult:float 

@dataclass
class TrendWithStopLossModel(IndicatorBase):
    fast_period :int 
    slow_period :int 
    signal_period :int 
    atr_length :int 
    atr_mamode :str 
    atr_multiplier:float 


@dataclass         
class DonchainModel(IndicatorBase):
    lower_length:int 
    upper_length:int 

@dataclass         
class KeltnerChannelsModel(IndicatorBase):
    length:int 

@dataclass         
class ATKBOTModel(IndicatorBase):
    key_value_long:float
    key_value_short:float
    atr_long_period:float
    ema_long_period:int
    atr_short_period:float
    ema_short_period:int

@dataclass         
class UTBOTModel(IndicatorBase):
    key_value_long:float
    key_value_short:float
    atr_long_period:float
    ema_long_period:int
    atr_short_period:float
    ema_short_period:int

@dataclass         
class SMCModel(IndicatorBase):
    window:int
    swing_length:int
    time_frame:str
    session:str

    
@dataclass 
class UTBOTWITHBBModel(IndicatorBase):
    atr_length:int
    channel_length:int
    key_value:float
    atr_utbot_length:int
    mult:float
    wicks:bool
    band_type:str

    
@dataclass 
class ROCModel(IndicatorBase):
    source:str    
    length:int

@dataclass
class ROCModel(IndicatorBase):
    source:str    
    length:int 

@dataclass
class RSIModel(IndicatorBase):
    source:str    
    length:int 
    mamode:str 

@dataclass
class EMATRENDMETTERModel(IndicatorBase):
    base_ema_length:int
    ema_length_1:int
    ema_length_2:int
    ema_length_3:int

@dataclass
class MOMModel(IndicatorBase):
    source:str    
    length:int 

@dataclass
class CCIModel(IndicatorBase):
    length:int 
    c:float     


@dataclass    
class STCModel(IndicatorBase):
    source:str   
    tclength:int
    fast:int 
    slow:int 
    mamode:str 

@dataclass
class STOCHModel(IndicatorBase):
    smooth_k_period:int 
    k_period:int 
    d_period:int 
    mamode:str 

@dataclass
class STOCHRSIModel(IndicatorBase):
    rsi_period:int 
    period:int
    k_period:int
    d_period:int 
    source:str 
    mamode:str 

@dataclass 
class VORTEXModel(IndicatorBase):
    period :int
    drift :int

@dataclass
class TRIXModel(IndicatorBase):
    length_period :int 
    signal_period:int 
    source:str 
    mamode:str

@dataclass          
class TSIModel(IndicatorBase):
    fast_period :int 
    slow_period :int 
    signal_period:int 
    source:str 
    mamode:str 

@dataclass          
class RGVIModel(IndicatorBase):
    length :int 
    swma_length :int 

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


@dataclass
class SuperTrendModel(IndicatorBase):
    length :int
    atr_length :int
    multiplier :float
    atr_mamode :str

@dataclass
class SuperWithSlModel(IndicatorBase):
    supertrend_length :int
    supertrend_atr_length:int
    supertrend_multiplier :float
    supertrend_atr_mamode :str
    atr_length :int
    atr_mamode :str
    atr_multiplier :float
