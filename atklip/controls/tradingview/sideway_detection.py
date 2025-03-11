import numpy as np
import pandas as pd

# Sample OHLC data (replace with real data)
data = pd.DataFrame({
    'open': np.random.random(500),
    'high': np.random.random(500),
    'low': np.random.random(500),
    'close': np.random.random(500)
})

# Inputs
bars_min_in_sideway = 5  # Minimum bars in Sideway
bars_ext_for_sideway = 2  # Extend bars for Sideway
percent_change_sideway = 2.0  # Percent change to form Sideway
recommended_settings = True

# Adjust percent_change_sideway based on timeframe
if recommended_settings:
    chart_timeframe_minutes = 60  # Example timeframe in minutes
    if chart_timeframe_minutes == 1:
        percent_change_sideway = 0.1
    elif chart_timeframe_minutes == 5:
        percent_change_sideway = 0.1
    elif chart_timeframe_minutes == 10:
        percent_change_sideway = 0.15
    elif chart_timeframe_minutes == 15:
        percent_change_sideway = 0.25
    elif chart_timeframe_minutes == 30:
        percent_change_sideway = 0.5
    elif chart_timeframe_minutes == 60:
        percent_change_sideway = 0.75
    elif chart_timeframe_minutes == 60 * 24:
        percent_change_sideway = 4.0
    elif chart_timeframe_minutes == 60 * 24 * 7:
        percent_change_sideway = 10.0
    elif chart_timeframe_minutes > 60 * 24 * 7:
        percent_change_sideway = 20.0

# Initialize variables
is_new_sideway = False
new_sideway_x = 0
new_sideway_y = 0.0
new_sideway_high = 0.0
sideway_boxes = []

# Loop through data to find sideways zones
for i in range(bars_min_in_sideway, len(data)):
    bar_cur_mid_price = abs(data.loc[i, 'open'] - data.loc[i, 'close']) / 2 + min(data.loc[i, 'open'], data.loc[i, 'close'])

    if is_new_sideway:
        pc = abs(100 - abs(new_sideway_y * 100 / bar_cur_mid_price))

        if pc > percent_change_sideway:
            # Save the current sideway box
            sideway_boxes.append({
                'start': new_sideway_x,
                'end': i + bars_ext_for_sideway,
                'top': new_sideway_y + new_sideway_high,
                'bottom': new_sideway_y - new_sideway_high
            })

            # Reset the forming sideway box
            is_new_sideway = False
        else:
            # Update the current sideway box
            new_sideway_x = i - bars_min_in_sideway
            new_sideway_y = bar_cur_mid_price
            new_sideway_high = bar_cur_mid_price * percent_change_sideway / 100

    else:
        is_new_sideway = True
        for j in range(1, bars_min_in_sideway + 1):
            bar_pre_mid_price = abs(data.loc[i - j, 'open'] - data.loc[i - j, 'close']) / 2 + min(data.loc[i - j, 'open'], data.loc[i - j, 'close'])
            pc = abs(100 - abs(bar_pre_mid_price * 100 / bar_cur_mid_price))
            if pc > percent_change_sideway:
                is_new_sideway = False
                break

        if is_new_sideway:
            new_sideway_x = i - bars_min_in_sideway
            new_sideway_y = bar_cur_mid_price
            new_sideway_high = bar_cur_mid_price * percent_change_sideway / 100

# Output the detected sideway zones
print("Detected Sideways Zones:")
for box in sideway_boxes:
    print(f"Start: {box['start']}, End: {box['end']}, Top: {box['top']}, Bottom: {box['bottom']}")
