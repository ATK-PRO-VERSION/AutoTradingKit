import datetime as dt
from math import floor
import re
from numba import jit,njit
from typing import List
from typing import Union
import numpy as np


def round_(v):
    return np.floor(v+0.5)

def convert_precision(number):
    if number >= 1:
        return int(number)
    number = f"{number}"
    if "1e" in number:
        return int(number[-2:])
    decimal_part = number.split('.')[1]  
    return len(decimal_part)

def mouse_clicked(vb, ev):
    if ev.button() == 8: # back
        vb.pan_x(percent=-30)
    elif ev.button() == 16: # fwd
        vb.pan_x(percent=+30)
    else:
        return False
    return True

def xminmax(datasrc, x_indexed, init_steps=None, extra_margin=0):
    side_margin = 0.5
    right_margin_candles = 100  # whitespace at the right-hand side
    if x_indexed and init_steps:
        # initial zoom
        x0 = max(len(datasrc) - init_steps, 0) - side_margin - extra_margin
        x1 = len(datasrc) + right_margin_candles + side_margin + extra_margin
    elif x_indexed:
        # total x size for indexed data
        x0 = -side_margin - extra_margin
        x1 = len(datasrc) + right_margin_candles - 1 + side_margin + extra_margin  # add another margin to get the "snap back" sensation
    else:
        # x size for plain Y-over-X data (i.e. not indexed)
        x0 = min(datasrc)
        x1 = max(datasrc)
        # extend margin on decoupled plots
        d = (x1 - x0) * (0.2 + extra_margin)
        x0 -= d
        x1 += d
    return x0, x1

def find_nearest_index(lst, special_value):
        index = min(range(len(lst)), key=lambda i: abs(lst[i] - special_value))
        return index
@njit(cache=True)
def percent_caculator(start, stop):
    percent = float(((float(start) - float(stop)) / float(start))) * 100
    if percent > 0:
        return percent
    else:
        return abs(percent)

@jit(nopython=True)
def binary_search(x,arr,length):
    left = 0
    right = length - 1
    while left <= right:
        mid = (left + right) // 2
        if arr[mid] == x:
            return mid
        elif arr[mid] < x:
            left = mid + 1
        else:
            right = mid - 1

    if right < 0:
        return 0
    if left >= length:
        return length - 1
    if abs(arr[right] - x) <= abs(arr[left] - x):
        return right
    else:
        return left

@njit(cache=True)
def supersmoother_fast(source, period):
    if not isinstance(source,np.ndarray):
        source = np.array(source)
    a = np.exp(-1.414 * np.pi / period)
    b = 2 * a * np.cos(1.414 * np.pi / period)
    newseries = np.copy(source)
    for i in range(2, source.shape[0]):
        newseries[i] = (1 + a ** 2 - b) / 2 * (source[i] + source[i - 1]) \
                       + b * newseries[i - 1] - a ** 2 * newseries[i - 2]
    return newseries


def change_float_to_date_local(timestamp):
    date_time = dt.datetime.fromtimestamp(float(timestamp))
    d = date_time.strftime("%Y-%m-%d %H:%M:%S")
    return d

def covert_time_to_sec(string):
    count = 60
    if "m" in string:
        count = 60
    elif "h" in string:
        count = 60*60
    elif "d" in string:
        count = 24*60*60
    elif "w" in string:
        count = 24*60*60*7
    elif "M" in string:
        count = 24*60*60*30
    match = re.search(r"[-+]?\d*\.\d+|\d+", string)
    if match:
        _value = float(match.group())
        kq = count*_value
        # #print(kq)  
        return kq
    return count

def timestamptodate(timestamp):
        from datetime import datetime
        return datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:%M:%S")

