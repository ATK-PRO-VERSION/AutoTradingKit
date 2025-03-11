import numpy as np
import pandas as pd
import pandas_ta as ta

def chandelier_exit(data: pd.DataFrame, atr_period: int = 22, atr_multiplier: float = 3.0, use_close: bool = True):
    """
    Implements the Chandelier Exit logic.

    Parameters:
        data (pd.DataFrame): DataFrame with 'open', 'high', 'low', 'close' columns.
        atr_period (int): Period for ATR calculation.
        atr_multiplier (float): Multiplier for ATR.
        use_close (bool): Whether to use the close price for extremums.

    Returns:
        pd.DataFrame: DataFrame with Chandelier Exit calculations.
    """
    # Calculate ATR
    data['atr'] = atr_multiplier * ta.atr(data['high'], data['low'], data['close'], length=atr_period)

    # Calculate long stop
    if use_close:
        data['highest_close'] = data['close'].rolling(window=atr_period).max()
    else:
        data['highest_high'] = data['high'].rolling(window=atr_period).max()
    data['long_stop'] = (data['highest_close'] if use_close else data['highest_high']) - data['atr']
    data['long_stop_prev'] = data['long_stop'].shift(1)
    data['long_stop'] = np.where(data['close'].shift(1) > data['long_stop_prev'],
                                 np.maximum(data['long_stop'], data['long_stop_prev']),
                                 data['long_stop'])

    # Calculate short stop
    if use_close:
        data['lowest_close'] = data['close'].rolling(window=atr_period).min()
    else:
        data['lowest_low'] = data['low'].rolling(window=atr_period).min()
    data['short_stop'] = (data['lowest_close'] if use_close else data['lowest_low']) + data['atr']
    data['short_stop_prev'] = data['short_stop'].shift(1)
    data['short_stop'] = np.where(data['close'].shift(1) < data['short_stop_prev'],
                                  np.minimum(data['short_stop'], data['short_stop_prev']),
                                  data['short_stop'])

    # Determine trend direction
    data['dir'] = 1  # Default direction
    data['dir'] = np.where(data['close'] > data['short_stop_prev'], 1,
                           np.where(data['close'] < data['long_stop_prev'], -1, data['dir'].shift(1)))

    # Signals
    data['buy_signal'] = (data['dir'] == 1) & (data['dir'].shift(1) == -1)
    data['sell_signal'] = (data['dir'] == -1) & (data['dir'].shift(1) == 1)

    # Final result
    result = data[['atr', 'long_stop', 'short_stop', 'dir', 'buy_signal', 'sell_signal']]
    return result
