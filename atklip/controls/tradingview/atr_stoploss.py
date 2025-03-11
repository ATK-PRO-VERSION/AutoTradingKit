import pandas as pd
import numpy as np
import atklip.controls as ta

def ma_function(source, length, smoothing):
    if smoothing == "RMA":
        return ta.rma(source, length)
    elif smoothing == "SMA":
        return ta.sma(source, length)
    elif smoothing == "EMA":
        return ta.ema(source, length)
    elif smoothing == "WMA":
        return ta.wma(source, length)
    else:
        return ta.rma(source, length)  # Default to RMA nếu không có lựa chọn

def atr_stoploss(df:pd.DataFrame,length = 14,
                    smoothing = "RMA",
                    multiplier = 1.5):
    """_summary_
    Args:
        _df (pd.DataFrame): df = {
                                'open': np.random.uniform(100, 200, 100),
                                'high': np.random.uniform(150, 250, 100),
                                'low': np.random.uniform(50, 100, 100),
                                'close': np.random.uniform(100, 200, 100),
                                }
        length (int, optional): _description_. Defaults to 14.
        smoothing (str, optional): _description_. Defaults to "RMA".
        multiplier (float, optional): _description_. Defaults to 1.5.
    Returns:
        _type_: _description_
    """
    # df = _df.copy()
    src1 = df['high']
    src2 = df['low']
    # Tính toán ATR (Average True Range)
    df['tr'] = ta.true_range(df['high'], df['low'], df['close'])
    df['atr'] = ma_function(df['tr'], length, smoothing)
    # Tính toán các giá trị cho stop loss
    df['a'] = df['atr'] * multiplier
    df['short_stoploss'] = df['a'] + src1  # ATR Short Stop Loss
    df['long_stoploss'] = src2 - df['a']  # ATR Long Stop Loss
    return df

