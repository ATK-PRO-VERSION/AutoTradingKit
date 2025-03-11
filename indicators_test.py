import numpy as np
import pandas as pd
import pandas_ta as ta

from atklip.app_utils.helpers import crossover

def utsignal(data,a,c):
    # ATR Calculation
    xATR = ta.atr(data["high"], data["low"], data["close"], length=c)
    nLoss = a * xATR
    src = data["close"]
    # ATR Trailing Stop
    xATRTrailingStop = np.zeros(len(data))
    for i in range(1, len(data)):
        if src[i] > xATRTrailingStop[i - 1] and src[i - 1] > xATRTrailingStop[i - 1]:
            xATRTrailingStop[i] = max(xATRTrailingStop[i - 1], src[i] - nLoss[i])
        elif src[i] < xATRTrailingStop[i - 1] and src[i - 1] < xATRTrailingStop[i - 1]:
            xATRTrailingStop[i] = min(xATRTrailingStop[i - 1], src[i] + nLoss[i])
        else:
            xATRTrailingStop[i] = src[i] - nLoss[i] if src[i] > xATRTrailingStop[i - 1] else src[i] + nLoss[i]
    # EMA for crossover logic
    ema = ta.ema(src, length=1)
    # above = (ema > xATRTrailingStop).astype(int).diff() > 0
    # below = (xATRTrailingStop > ema).astype(int).diff() > 0
    above = crossover(ema, xATRTrailingStop)
    below = crossover(xATRTrailingStop, ema)
    return src, xATRTrailingStop, above, below

# Bands Calculation
def calculate_bands(data, band_type, length, std_dev):
    if band_type == "Bollinger Bands":
        bb = ta.bbands(data["close"], length=length, std=std_dev)
        _props = f"_{length}_{std_dev}"
        lower_name = f"BBL{_props}"
        mid_name = f"BBM{_props}"
        upper_name = f"BBU{_props}"
        return bb[lower_name], bb[mid_name], bb[upper_name]
    elif band_type == "Keltner Channel":
        kc = ta.kc(data, length=length)
        return kc["KCL_20"], kc["KCM_20"], kc["KCU_20"]
    elif band_type == "Donchian Channel":
        dc_high = data["high"].rolling(window=length).max()
        dc_low = data["low"].rolling(window=length).min()
        return dc_low, (dc_high + dc_low) / 2, dc_high
    else:
        return None, None, None

# Trailing Stop Calculation
def calculate_trailing_stop(data:pd.DataFrame, lower:pd.Series, upper:pd.Series, atr_length:int, mult: float, wicks: bool):
    if lower is None or upper is None:
        raise ValueError("Invalid band type or parameters resulting in None values for bands.")
    
    atr = ta.atr(data["high"], data["low"], data["close"], length=atr_length)
    
    _dir = np.ones(len(data))
    dir = pd.Series(_dir)
    
    if wicks:
        longtarget = data["low"]
        shorttarget = data["high"]
    else:
        shorttarget = data["close"]
        longtarget = data["close"]
    
    long_stop = lower - atr * mult
    short_stop = upper + atr * mult
    
    short_stop_pre = short_stop.shift(1)
    long_stop_pre = long_stop.shift(1)
    
    for i in range(1, len(data)):
        if dir[i - 1] == 1 and longtarget[i] > long_stop_pre[i]:
            dir[i] = -1
        elif dir[i - 1] == -1 and shorttarget[i] < short_stop_pre[i]:
            dir[i] = 1
        else:
            dir[i] = dir[i - 1]
    return dir, long_stop, short_stop

def utbot_with_bb(data,a = 1,c=10, mult = 1, wicks=False,band_type = "Bollinger Bands",atr_length=22, channel_length = 20, StdDev = 1):
    """_summary_
    Args:
        data (_type_): _description_
        a (int, optional): Key Value, this changes sensitivity. Defaults to 1.
        c (int, optional): ATR Period. Defaults to 10.
        mult (int, optional): ATR Multiplier. Defaults to 1.
        wicks (bool, optional): _description_. Defaults to False.
        band_type (str, optional): Channel Type. Defaults to "Bollinger Bands".
        channel_length (int, optional): _description_. Defaults to 20.
        StdDev (int, optional): _description_. Defaults to 1.
    Returns:
        _type_: _description_
    """
    data = data.copy()

    src, xATRTrailingStop, above, below = utsignal(data,a,c)
    lower_band, middle_band, upper_band = calculate_bands(data, band_type, channel_length, StdDev)
    
    barState, buyStop, sellStop = calculate_trailing_stop(data, lower_band, upper_band, atr_length, mult, wicks)
    # Trade Conditions
    buy_condition = (src > xATRTrailingStop) & above & (barState == 1)
    sell_condition = (src < xATRTrailingStop) & below & (barState == -1)
    # Output Results
    data["BuySignal"] = buy_condition
    data["SellSignal"] = sell_condition
    
    return data[["BuySignal", "SellSignal"]]

# Sample OHLC Data (replace with real data)
data = pd.DataFrame({
    "open": np.random.random(100),
    "high": np.random.random(100),
    "low": np.random.random(100),
    "close": np.random.random(100)
})

data = utbot_with_bb(data)

print(data.loc[(data["BuySignal"]==True)|(data["SellSignal"]==True)])