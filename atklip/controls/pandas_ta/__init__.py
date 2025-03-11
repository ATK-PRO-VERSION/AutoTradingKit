"""
.. moduleauthor:: Kevin Johnson
"""
name = "pandas_ta"

# Dictionaries and version
from atklip.controls.pandas_ta.maps import EXCHANGE_TZ, RATE, Category, Imports
from atklip.controls.pandas_ta.utils import *
from atklip.controls.pandas_ta.utils import __all__ as utils_all

from atklip.controls.pandas_ta.overlap import *
from atklip.controls.pandas_ta.overlap import __all__ as overlap_all


__all__ = [
    "name",
    "EXCHANGE_TZ",
    "RATE",
    "Category",
    "Imports",
    utils_all
    + overlap_all
]
