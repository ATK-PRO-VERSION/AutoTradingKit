from pydantic import BaseModel

from atklip.controls.ma_type import IndicatorType


class CandleInfor(BaseModel):
    """_summary_
    Args:
        name = ["japancandle","smoothcandle","supersmoothcandle","heikinashi"]
        source = {"japan", "heikin"}
    """
    id_exchange:str
    symbol:str
    interval:str
    ma_type:IndicatorType
    ma_leng:int
    n_smooth:int
    name:str
    source:str
    precicion:float
    
class IndicatorInfor(BaseModel):
    """_summary_
    Args:
        source = {"japan", "heikin"}
    """
    name:str
    id_exchange:str
    source:str
    symbol:str
    interval:str
    precicion:float

class ZigzagModel(IndicatorInfor):
    legs:int
    devision:float

