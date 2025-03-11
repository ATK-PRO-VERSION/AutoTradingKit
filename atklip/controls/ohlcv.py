"""Collection of classes related to `OHLCV` input type."""

from dataclasses import dataclass
from datetime import datetime
from itertools import zip_longest
from typing import List, Dict, Optional


@dataclass
class OHLCV:
    open: Optional[float]
    high: Optional[float]
    low: Optional[float]
    close: Optional[float]
    hl2: Optional[float]
    hlc3: Optional[float]
    ohlc4: Optional[float]
    volume: Optional[float]
    time: Optional[int] 
    index: Optional[int]  
