from enum import Enum
from atklip.controls import ZIGZAG, MACD, BBANDS, DONCHIAN, ROC, RSI, SMOOTH_CANDLE, STC, STOCH, STOCHRSI, VORTEX, MA,\
    TRIX,TSI,UO,N_SMOOTH_CANDLE,JAPAN_CANDLE,HEIKINASHI

from atklip.controls import PD_MAType,IndicatorType,OHLCV

from atklip.exchanges import CryptoExchange,CryptoExchange_WS,Exchange

class EnumIndicator(Enum):
    "smoothcandle"=SMOOTH_CANDLE
    "japancandle"=JAPAN_CANDLE
    "supersmoothcandle"=N_SMOOTH_CANDLE
    "heikinashi"=HEIKINASHI
    "stc"=STC
    "stoch"=STOCH 
    "stochrsi"=STOCHRSI 
    "vortex"=VORTEX 
    "ma"=MA
    "trix"=TRIX
    "tsi"=TSI
    "uo"=UO
    "zigzag"= ZIGZAG
    "macd"=MACD
    "bband"=BBANDS
    "donchain"=DONCHIAN
    "roc"=ROC
    "rsi"=RSI
    


