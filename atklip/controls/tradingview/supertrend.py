import numpy as np
import pandas as pd
import pandas_ta as ta

def supertrend(data, atr_period=10, multiplier=3.0, change_atr=True):
    """
    Supertrend calculation in Python.
    
    Parameters:
    - data: DataFrame with columns ["high", "low", "close", "hl2"].
    - atr_period: ATR calculation period.
    - multiplier: ATR multiplier for upper/lower bands.
    - change_atr: Boolean to switch ATR calculation method.
    
    Returns:
    - DataFrame with calculated Supertrend columns.
    """
    # Calculate ATR
    if change_atr:
        atr = ta.atr(data["high"], data["low"], data["close"], length=atr_period)
    else:
        true_range = data["high"] - data["low"]
        atr = true_range.rolling(atr_period).mean()
    
    # Source price (hl2)
    src = data["hl2"]

    # Calculate Upper and Lower Bands
    upper_band = src - (multiplier * atr)
    lower_band = src + (multiplier * atr)

    # Initialize columns
    up = upper_band.copy()
    dn = lower_band.copy()
    trend = np.ones(len(data), dtype=int)  # Start with uptrend

    # Calculate trend direction
    for i in range(1, len(data)):
        up[i] = max(up[i], up[i - 1]) if data["close"].iloc[i - 1] > up[i - 1] else up[i]
        dn[i] = min(dn[i], dn[i - 1]) if data["close"].iloc[i - 1] < dn[i - 1] else dn[i]
        if trend[i - 1] == -1 and data["close"].iloc[i] > dn[i - 1]:
            trend[i] = 1
        elif trend[i - 1] == 1 and data["close"].iloc[i] < up[i - 1]:
            trend[i] = -1
        else:
            trend[i] = trend[i - 1]

    # Create buy/sell signals
    buy_signal = (trend == 1) & (np.roll(trend, 1) == -1)
    sell_signal = (trend == -1) & (np.roll(trend, 1) == 1)

    # Add results to DataFrame
    data["Supertrend_Up"] = np.where(trend == 1, up, np.nan)
    data["Supertrend_Down"] = np.where(trend == -1, dn, np.nan)
    data["Trend"] = trend
    data["Buy_Signal"] = buy_signal
    data["Sell_Signal"] = sell_signal

    return data

# Example usage
if __name__ == "__main__":
    # Simulated DataFrame with OHLC data
    data = pd.DataFrame({
        "high": [10, 12, 11, 15, 14, 13],
        "low": [8, 9, 8, 10, 10, 9],
        "close": [9, 11, 10, 14, 12, 10]
    })
    data["hl2"] = (data["high"] + data["low"]) / 2

    # Calculate Supertrend
    result = supertrend(data, atr_period=10, multiplier=3.0, change_atr=True)

    # Display result
    print(result)
