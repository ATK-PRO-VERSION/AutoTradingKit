"""
.. moduleauthor:: Kevin Johnson
"""
name = "pandas_ta"

# Dictionaries and version
from atklip.controls.pandas_ta.maps import EXCHANGE_TZ, RATE, Category, Imports
from atklip.controls.pandas_ta.utils import *

from atklip.controls.pandas_ta.overlap import *

from atklip.controls.pandas_ta.candles import *
from atklip.controls.pandas_ta.cycles import *
from atklip.controls.pandas_ta.momentum import *
from atklip.controls.pandas_ta.overlap import *
from atklip.controls.pandas_ta.performance import *
from atklip.controls.pandas_ta.statistics import *
from atklip.controls.pandas_ta.transform import *
from atklip.controls.pandas_ta.trend import *
from atklip.controls.pandas_ta.volatility import *
from atklip.controls.pandas_ta.volume import *