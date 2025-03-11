import pandas as pd
import pandas_ta as ta
import numpy as np

# Constants
BULLISH_LEG = 1
BEARISH_LEG = 0

BULLISH = 1
BEARISH = -1

# Data Structures
class Alerts:
    def __init__(self):
        self.internalBullishBOS = False
        self.internalBearishBOS = False
        self.internalBullishCHoCH = False
        self.internalBearishCHoCH = False
        self.swingBullishBOS = False
        self.swingBearishBOS = False
        self.swingBullishCHoCH = False
        self.swingBearishCHoCH = False
        self.internalBullishOrderBlock = False
        self.internalBearishOrderBlock = False
        self.swingBullishOrderBlock = False
        self.swingBearishOrderBlock = False
        self.equalHighs = False
        self.equalLows = False
        self.bullishFairValueGap = False
        self.bearishFairValueGap = False

class TrailingExtremes:
    def __init__(self):
        self.top = np.nan
        self.bottom = np.nan
        self.barTime = 0
        self.barIndex = 0
        self.lastTopTime = 0
        self.lastBottomTime = 0

class FairValueGap:
    def __init__(self, top, bottom, bias):
        self.top = top
        self.bottom = bottom
        self.bias = bias

class Trend:
    def __init__(self, bias):
        self.bias = bias

class Pivot:
    def __init__(self, currentLevel, lastLevel, crossed, barTime, barIndex):
        self.currentLevel = currentLevel
        self.lastLevel = lastLevel
        self.crossed = crossed
        self.barTime = barTime
        self.barIndex = barIndex

class OrderBlock:
    def __init__(self, barHigh, barLow, barTime, bias):
        self.barHigh = barHigh
        self.barLow = barLow
        self.barTime = barTime
        self.bias = bias

# Variables
swingHigh = Pivot(np.nan, np.nan, False, 0, 0)
swingLow = Pivot(np.nan, np.nan, False, 0, 0)
internalHigh = Pivot(np.nan, np.nan, False, 0, 0)
internalLow = Pivot(np.nan, np.nan, False, 0, 0)
equalHigh = Pivot(np.nan, np.nan, False, 0, 0)
equalLow = Pivot(np.nan, np.nan, False, 0, 0)
swingTrend = Trend(0)
internalTrend = Trend(0)
fairValueGaps = []
parsedHighs = []
parsedLows = []
highs = []
lows = []
times = []
trailing = TrailingExtremes()
swingOrderBlocks = []
internalOrderBlocks = []
currentAlerts = Alerts()

# Functions
def leg(size, high, low):
    leg_value = 0
    newLegHigh = high[size] > high.rolling(size).max()
    newLegLow = low[size] < low.rolling(size).min()
    
    if newLegHigh:
        leg_value = BEARISH_LEG
    elif newLegLow:
        leg_value = BULLISH_LEG
    return leg_value

def startOfNewLeg(leg):
    return leg.diff() != 0

def startOfBearishLeg(leg):
    return leg.diff() == -1

def startOfBullishLeg(leg):
    return leg.diff() == 1

def getCurrentStructure(size, equalHighLow=False, internal=False, high=None, low=None, time=None, bar_index=None):
    currentLeg = leg(size, high, low)
    newPivot = startOfNewLeg(currentLeg)
    pivotLow = startOfBullishLeg(currentLeg)
    pivotHigh = startOfBearishLeg(currentLeg)

    if newPivot:
        if pivotLow:
            pivot = equalLow if equalHighLow else (internalLow if internal else swingLow)
            pivot.lastLevel = pivot.currentLevel
            pivot.currentLevel = low[size]
            pivot.crossed = False
            pivot.barTime = time[size]
            pivot.barIndex = bar_index[size]

            if not equalHighLow and not internal:
                trailing.bottom = pivot.currentLevel
                trailing.barTime = pivot.barTime
                trailing.barIndex = pivot.barIndex
                trailing.lastBottomTime = pivot.barTime
        else:
            pivot = equalHigh if equalHighLow else (internalHigh if internal else swingHigh)
            pivot.lastLevel = pivot.currentLevel
            pivot.currentLevel = high[size]
            pivot.crossed = False
            pivot.barTime = time[size]
            pivot.barIndex = bar_index[size]

            if not equalHighLow and not internal:
                trailing.top = pivot.currentLevel
                trailing.barTime = pivot.barTime
                trailing.barIndex = pivot.barIndex
                trailing.lastTopTime = pivot.barTime

def displayStructure(internal=False, close=None, high=None, low=None, time=None, bar_index=None):
    pivot = internalHigh if internal else swingHigh
    trend = internalTrend if internal else swingTrend

    if close[-1] > pivot.currentLevel and not pivot.crossed:
        tag = 'BOS' if trend.bias == BEARISH else 'CHOCH'
        pivot.crossed = True
        trend.bias = BULLISH

    pivot = internalLow if internal else swingLow
    if close[-1] < pivot.currentLevel and not pivot.crossed:
        tag = 'BOS' if trend.bias == BULLISH else 'CHOCH'
        pivot.crossed = True
        trend.bias = BEARISH

def updateTrailingExtremes(high, low, time):
    trailing.top = max(high, trailing.top)
    trailing.lastTopTime = time if trailing.top == high else trailing.lastTopTime
    trailing.bottom = min(low, trailing.bottom)
    trailing.lastBottomTime = time if trailing.bottom == low else trailing.lastBottomTime

# Example usage with pandas DataFrame
def process_data(df):
    df['leg'] = df.apply(lambda row: leg(5, df['high'], df['low']), axis=1)
    df['newPivot'] = startOfNewLeg(df['leg'])
    df['pivotLow'] = startOfBullishLeg(df['leg'])
    df['pivotHigh'] = startOfBearishLeg(df['leg'])

    for i in range(len(df)):
        getCurrentStructure(5, False, False, df['high'], df['low'], df['time'], df.index)
        displayStructure(False, df['close'], df['high'], df['low'], df['time'], df.index)
        updateTrailingExtremes(df['high'][i], df['low'][i], df['time'][i])

# Load your data into a pandas DataFrame
# df = pd.read_csv('your_data.csv')
# process_data(df)