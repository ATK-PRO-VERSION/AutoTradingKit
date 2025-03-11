import pandas as pd
import numpy as np
TA_EPSILON = 1e-10

def real_body(open_, high, low, close):
    """实体"""
    return (close - open_).abs()

def upper_shadow(open_, high, low, close):
    """上影"""
    return high - pd.DataFrame([open_, close]).max()

def lower_shadow(open_, high, low, close):
    """下影"""
    return pd.DataFrame([open_, close]).min() - low

def high_low_range(open_, high, low, close):
    """总长"""
    return high - low

def upper_body(open_, high, low, close):
    """实体上沿"""
    return pd.DataFrame([open_, close]).max()

def lower_body(open_, high, low, close):
    """实体下沿"""
    return pd.DataFrame([open_, close]).min()

def shadows(open_, high, low, close):
    """阴影"""
    return high_low_range(open_, high, low, close) - real_body(open_, high, low, close)

def efficiency_ratio(open_, high, low, close):
    """市场效率"""
    displacement = real_body(open_, high, low, close)
    distance = 2 * high_low_range(open_, high, low, close) - displacement
    return displacement / (distance + TA_EPSILON)

def candle_color(open_, high, low, close):
    """K线颜色"""
    return close >= open_

def four_price_doji(open_, high, low, close):
    """一字"""
    return low >= (high - TA_EPSILON)

def doji(open_, high, low, close):
    """十字"""
    return (open_ - close).abs() <= TA_EPSILON

def dragonfly(open_, high, low, close):
    """正T字"""
    return doji(open_, high, low, close) & (low < close - TA_EPSILON)

def gravestone(open_, high, low, close):
    """倒T字"""
    return doji(open_, high, low, close) & (high > close + TA_EPSILON)

# Hàm upper_body và lower_body có thể được định nghĩa tương tự hoặc sử dụng từ trước

def ts_gap_up(open_, high, low, close):
    """跳空高开 - Gap up"""
    return low > high.shift(1)

def ts_gap_down(open_, high, low, close):
    """跳空低开 - Gap down"""
    return high < low.shift(1)

def ts_real_body_gap_up(open_, high, low, close):
    """实体跳空高开 - Real body gap up"""
    return lower_body(open_, high, low, close) > upper_body(open_, high, low, close).shift(1)

def ts_real_body_gap_down(open_, high, low, close):
    """实体跳空低开 - Real body gap down"""
    return upper_body(open_, high, low, close) < lower_body(open_, high, low, close).shift(1)

def limit_up(price, high_limit):
    return price >= high_limit - TA_EPSILON

def limit_up_at_open(open_, high, low, close, high_limit):
    return limit_up(open_, high_limit)

def limit_up_at_close(open_, high, low, close, high_limit):
    return limit_up(close, high_limit)

def limit_up_at_high(open_, high, low, close, high_limit):
    return (limit_up(high, high_limit)) & (~limit_up(close, high_limit))

def limit_up_four_price_doji(open_, high, low, close, high_limit):
    return (four_price_doji(open_, high, low, close)) & limit_up(close, high_limit)

def limit_up_dragonfly(open_, high, low, close, high_limit):
    return limit_up(close, high_limit) & dragonfly(open_, high, low, close)

def limit_down(price, low_limit):
    return price <= low_limit + TA_EPSILON

def limit_down_at_open(open_, high, low, close, low_limit):
    return limit_down(open_, low_limit)

def limit_down_at_close(open_, high, low, close, low_limit):
    return limit_down(close, low_limit)

def limit_down_at_high(open_, high, low, close, low_limit):
    return limit_down(low, low_limit) & ~limit_down(close, low_limit)

def limit_down_four_price_doji(open_, high, low, close, low_limit):
    return four_price_doji(open_, high, low, close) & limit_down(close, low_limit)

def limit_down_gravestone(open_, high, low, close, low_limit):
    return limit_down(open_, low_limit) & gravestone(open_, high, low, close)
