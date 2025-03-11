import numpy as np
import pandas as pd
import pandas_ta as ta

def calculate_smc_logic(data, swing_length=10, atr_length=50, history_length=20, box_width=2.5):
    """
    Calculate Supply/Demand Zones and Break of Structure (BOS) based on input data.

    Args:
        data (pd.DataFrame): DataFrame with 'high', 'low', 'close' columns.
        swing_length (int): Length for determining swing highs/lows.
        atr_length (int): Length for ATR calculation.
        history_length (int): Number of historical zones to keep.
        box_width (float): Width of the supply/demand zones.

    Returns:
        dict: Contains supply zones, demand zones, and BOS levels.
    """
    # ATR calculation
    data['atr'] = ta.atr(data['high'], data['low'], data['close'], length=atr_length)

    # Swing highs and lows
    data['swing_high'] = data['high'].rolling(window=swing_length * 2 + 1, center=True).apply(
        lambda x: x[swing_length] if x[swing_length] == max(x) else np.nan, raw=True
    )
    data['swing_low'] = data['low'].rolling(window=swing_length * 2 + 1, center=True).apply(
        lambda x: x[swing_length] if x[swing_length] == min(x) else np.nan, raw=True
    )

    # Initialize zones
    supply_zones = []
    demand_zones = []
    bos_levels = []

    def add_zone(zones, value, atr, box_type):
        atr_buffer = atr * (box_width / 10)
        if box_type == 'supply':
            zone = {'top': value, 'bottom': value - atr_buffer}
        elif box_type == 'demand':
            zone = {'top': value + atr_buffer, 'bottom': value}
        zones.append(zone)
        if len(zones) > history_length:
            zones.pop(0)

    # Identify supply/demand zones
    for i in range(len(data)):
        if not np.isnan(data['swing_high'].iloc[i]):
            add_zone(supply_zones, data['swing_high'].iloc[i], data['atr'].iloc[i], 'supply')
        if not np.isnan(data['swing_low'].iloc[i]):
            add_zone(demand_zones, data['swing_low'].iloc[i], data['atr'].iloc[i], 'demand')

        # Check for BOS
        if supply_zones and data['close'].iloc[i] > supply_zones[-1]['top']:
            bos_levels.append({'type': 'BOS_UP', 'level': supply_zones[-1]['top']})
            supply_zones.pop(-1)
        if demand_zones and data['close'].iloc[i] < demand_zones[-1]['bottom']:
            bos_levels.append({'type': 'BOS_DOWN', 'level': demand_zones[-1]['bottom']})
            demand_zones.pop(-1)

    return {
        'supply_zones': supply_zones,
        'demand_zones': demand_zones,
        'bos_levels': bos_levels
    }

# Example usage with a DataFrame
data = pd.DataFrame({
    'high': [1, 2, 3, 4, 3, 2, 1, 2, 3, 4, 5],
    'low': [0.5, 1, 1.5, 2, 1.5, 1, 0.5, 1, 1.5, 2, 2.5],
    'close': [0.8, 1.5, 2.5, 3.5, 2.8, 1.8, 1, 1.5, 2.5, 3.5, 4.5]
})

result = calculate_smc_logic(data)
print(result)
