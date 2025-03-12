import datetime as dt
import re
from typing import List
import numpy as np
from decimal import Decimal

def round_(v):
    return np.floor(v+0.5)

def convert_precision(number):
    decimal_part = Decimal(str(number)).normalize()  # Chuẩn hóa số
    return abs(decimal_part.as_tuple().exponent)  # Lấy số chữ số thập phân

def getspecialvalues(_type,last_candle:List):
    if _type == "close":
        return last_candle[-1].index, last_candle[-1].close
    elif _type == "open":
        return  last_candle[-1].index, last_candle[-1].open
    elif _type == "high":
        return  last_candle[-1].index, last_candle[-1].high
    elif _type == "low":
        return last_candle[-1].index, last_candle[-1].low
    elif _type == "hl2":
        return last_candle[-1].index, last_candle[-1].hl2
    elif _type == "hlc3":
        return last_candle[-1].index, last_candle[-1].hlc3
    elif _type == "ohlc4":
        return last_candle[-1].index, last_candle[-1].ohlc4
    elif _type == "volume":
        return last_candle[-1].index, last_candle[-1].volume
    else:
        return None,None
    
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
    
def cal_line_price_fibo(top, bot, percent, direct=1):
    diff = (top - bot) * percent
    if direct == 1:
        return top - diff
    return bot + diff

def divide_with_remainder(a, b):
    quotient, remainder = divmod(a, b)
    return quotient, remainder

def percent_caculator(start, stop):
    percent = ((start - stop) / start) * 100
    if percent > 0:
        return round(percent,4)
    else:
        return round(abs(percent),4)


def calculate_stoploss(_type,start, percent):
    if _type == "long":
        stop = start*(1-percent/100)
    else:
        stop = start*(1+percent/100)
    return stop

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



def calculate_pl_with_fees(entry_price: float, exit_price: float, 
                           capital=1000, proportion_closed=1, 
                           leverage: int=1, taker_fee: float=0, 
                           maker_fee: float=0, order_type: str="market",
                           is_stop_loss=False):
    """_summary_
    Args:
        entry_price (float): _description_
        exit_price (float): _description_
        capital (int, optional): _description_. Defaults to 1000.
        leverage (int, optional): _description_. Defaults to 5.
        proportion_closed (int, optional): _description_. Defaults to 1.
        taker_fee (float, optional): fee for market order. Defaults to 0.05.
        maker_fee (float, optional): fee for litmit order. Defaults to 0.02.
        order_type (str, optional): limit or market. Defaults to "market".
        is_stop_loss (bool, optional): if Fasle: calculate profit if True: calculate stop loss. Defaults to False.
    Returns:
        _type_: _description_
    """
    taker_fee = taker_fee/100
    maker_fee = maker_fee/100
    total_position_value = capital * leverage
    close_fee = 0
    if order_type == "market":
        open_fee = total_position_value * taker_fee
        if is_stop_loss:
            close_fee = total_position_value *taker_fee* proportion_closed
    else:
        open_fee = total_position_value * maker_fee
        if is_stop_loss:
            close_fee = total_position_value *maker_fee* proportion_closed

    price_difference = abs(entry_price - exit_price)
        
    percent_change = price_difference / entry_price
    leverage_gain = percent_change * leverage
    capital_gain = leverage_gain * capital * proportion_closed
    pl = capital_gain - open_fee * proportion_closed - close_fee
    return round(pl, 4)


def cal_pnl_with_fee(entry_price: float, exit_price: float, 
                           capital=1000, proportion_closed=1, 
                           leverage: int=1, taker_fee: float=0, 
                           maker_fee: float=0, order_type: str="market",order_side:str="long",
                           is_stop_loss=False):
    """_summary_
    Args:
        entry_price (float): _description_
        exit_price (float): _description_
        capital (int, optional): _description_. Defaults to 1000.
        leverage (int, optional): _description_. Defaults to 5.
        proportion_closed (int, optional): _description_. Defaults to 1.
        taker_fee (float, optional): fee for market order. Defaults to 0.05.
        maker_fee (float, optional): fee for litmit order. Defaults to 0.02.
        order_type (str, optional): limit or market. Defaults to "market".
        is_stop_loss (bool, optional): if Fasle: calculate profit if True: calculate stop loss. Defaults to False.
    Returns:
        _type_: _description_
    """
    taker_fee = taker_fee/100
    maker_fee = maker_fee/100
    total_position_value = capital * leverage
    close_fee = 0
    if order_type == "market":
        open_fee = total_position_value * taker_fee
        if is_stop_loss:
            close_fee = total_position_value *taker_fee* proportion_closed
    else:
        open_fee = total_position_value * maker_fee
        if is_stop_loss:
            close_fee = total_position_value *maker_fee* proportion_closed

    
    if order_side == "long":
        price_difference =  exit_price - entry_price
    else:
        price_difference = entry_price - exit_price
        
    percent_change = price_difference / entry_price
    leverage_gain = percent_change * leverage
    capital_gain = leverage_gain * capital * proportion_closed
    pl = capital_gain - open_fee * proportion_closed - close_fee
    return round(pl, 4)

def calculate_recommended_capital_base_on_risk(entry_price: float, stop_loss_price: float, 
                                  total_capital: float=1000, risk_percentage: float=2, 
                                  leverage: int=1, taker_fee: float=0, maker_fee: float=0, 
                                  order_type: str="market"):
    """_summary_

    Args:
        entry_price (float): _description_
        stop_loss_price (float): _description_
        total_capital (float, optional): total balance. Defaults to 1000.
        risk_percentage (float, optional): _description_. Defaults to 2.
        leverage (int, optional): _description_. Defaults to 5.
        taker_fee (float, optional): _description_. Defaults to 0.05.
        maker_fee (float, optional): _description_. Defaults to 0.02.
        order_type (str, optional): _description_. Defaults to "market".

    Returns:
        _type_: _description_
    """
    taker_fee = taker_fee/100
    maker_fee = maker_fee/100
    capital_to_risk = total_capital * (risk_percentage / 100)
    price_difference = abs(entry_price - stop_loss_price)
    percent_change_sl = price_difference / entry_price
    leveraged_loss_per_unit = percent_change_sl * leverage
    
    if order_type == "market":
        total_taker_fee = entry_price * leverage * taker_fee * 2
    else:
        total_taker_fee = entry_price * leverage * maker_fee * 2
    
    effective_loss_per_unit = leveraged_loss_per_unit + (total_taker_fee / (entry_price * leverage))
    recommended_capital = capital_to_risk / effective_loss_per_unit
    return round(recommended_capital, 4)


def calculate_recommended_capital_base_on_loss_capital(entry_price: float, stop_loss_price: float, 
                                                        loss_capital: float=1000, 
                                                        leverage: int=1, taker_fee: float=0, 
                                                        maker_fee: float=0, order_type: str="market"):
    """_summary_

    Args:
        entry_price (float): _description_
        stop_loss_price (float): _description_
        loss_capital (float, optional): _description_. Defaults to 1000.
        leverage (int, optional): _description_. Defaults to 5.
        taker_fee (float, optional): _description_. Defaults to 0.05.
        maker_fee (float, optional): _description_. Defaults to 0.02.
        order_type (str, optional): _description_. Defaults to "market".

    Returns:
        _type_: _description_
    """
    taker_fee = taker_fee/100
    maker_fee = maker_fee/100
    price_difference = abs(entry_price - stop_loss_price)
    percent_change_sl = price_difference / entry_price
    leveraged_loss_per_unit = percent_change_sl * leverage
    
    if order_type == "market":
        total_taker_fee = entry_price * leverage * taker_fee * 2
    else:
        total_taker_fee = entry_price * leverage * maker_fee * 2
    
    effective_loss_per_unit = leveraged_loss_per_unit + (total_taker_fee / (entry_price * leverage))
    
    # Tính số vốn khuyến nghị dựa trên số vốn có thể mất
    recommended_capital = loss_capital / effective_loss_per_unit
    return round(recommended_capital, 4)
