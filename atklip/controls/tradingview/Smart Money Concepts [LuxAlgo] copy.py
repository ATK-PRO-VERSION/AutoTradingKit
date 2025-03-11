import numpy as np
import pandas as pd
import pandas_ta as ta
import talib

# Input parameters
step = 0.6  # Diameter of circles
filter_vol = 2.0  # Volume threshold to filter points
leftBars = 15  # Number of bars to the left of the pivot
rightBars = leftBars
show_lvl = True  # Option to show levels

# Define scaling factors
xScale = 2.0
yScale = 0.5 * ta.atr(length=500)

# Define colors (not used in calculations)
upper_col = '#fda05e'
lower_col = '#2fd68e'

# Initialize arrays for storing points and levels
points = []
levels = []

# Function to calculate pivot high and pivot low
def calculate_pivothigh(high, leftBars, rightBars):
    pivot_high = np.zeros_like(high)
    for i in range(leftBars, len(high) - rightBars):
        if high[i] == np.max(high[i - leftBars:i + rightBars + 1]):
            pivot_high[i] = high[i]
    return pivot_high

def calculate_pivotlow(low, leftBars, rightBars):
    pivot_low = np.zeros_like(low)
    for i in range(leftBars, len(low) - rightBars):
        if low[i] == np.min(low[i - leftBars:i + rightBars + 1]):
            pivot_low[i] = low[i]
    return pivot_low

# Function to calculate normalized volume delta
def calculate_normalized_volume(volume, leftBars, rightBars):
    volume_ = volume.rolling(window=leftBars * 2).sum()
    min_vol = volume_.rolling(window=300).min()
    max_vol = volume_.rolling(window=300).max()
    reference_vol = np.percentile(volume_, 95)
    norm_vol = (volume_ / reference_vol) * 5
    return norm_vol

# Function to check if lines are crossed
def check_cross(arrayOfLines, close):
    for line in arrayOfLines:
        lineLevel = line['price']
        lineWasCrossed = np.sign(close.shift(1) - lineLevel) != np.sign(close - lineLevel)
        if lineWasCrossed:
            arrayOfLines.remove(line)

# Function to draw circles (not used in calculations)
def draw_circle(src, mult_x, mult_y, high, low, rightBars, bar_index):
    points.clear()
    angle = 0
    source = high[rightBars] if src else low[rightBars]
    color = upper_col if src else lower_col

    for i in range(1, 12):
        xValue = int(np.round(xScale * mult_x * np.sin(angle))) + bar_index - rightBars
        yValue = yScale * mult_y * np.cos(angle) + source
        angle += np.pi / 5
        points.append((xValue, yValue))

# Function to draw levels (not used in calculations)
def draw_level(src, n, width, color):
    levels.append({'price': src, 'width': width, 'color': color})

# Main function to process data
def process_data(df):
    high = df['high']
    low = df['low']
    close = df['close']
    volume = df['volume']

    ph = calculate_pivothigh(high, leftBars, rightBars)
    pl = calculate_pivotlow(low, leftBars, rightBars)
    norm_vol = calculate_normalized_volume(volume, leftBars, rightBars)

    # Plotting logic for high pivots
    for i in range(11):
        condition = ~np.isnan(ph) & (norm_vol > i) & (norm_vol > filter_vol)
        if condition.iloc[-1]:
            draw_circle(True, np.round(i * step), np.round(i * step), high, low, rightBars, len(df) - 1)

    if ~np.isnan(ph.iloc[-1]) & (norm_vol.iloc[-1] > filter_vol):
        n = len(df) - 1 - rightBars
        src = high.iloc[-rightBars - 1]
        draw_level(src, n, 1, upper_col)

    # Plotting logic for low pivots
    for i in range(11, 0, -1):
        condition = ~np.isnan(pl) & (norm_vol > i) & (norm_vol > filter_vol)
        if condition.iloc[-1]:
            draw_circle(False, np.round(i * step), np.round(i * step), high, low, rightBars, len(df) - 1)

    if ~np.isnan(pl.iloc[-1]) & (norm_vol.iloc[-1] > filter_vol):
        n = len(df) - 1 - rightBars
        src = low.iloc[-rightBars - 1]
        draw_level(src, n, 1, lower_col)

    # Check and update crosses
    check_cross(levels, close)

    # Clean up lines if levels are not shown
    if not show_lvl:
        levels.clear()

# Example usage
# df = pd.read_csv('your_data.csv')  # Load your data here
# process_data(df)