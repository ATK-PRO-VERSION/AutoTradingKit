def real_body(open,close):
    return abs(close-open)
# Define a function to calculate the real body of a candlestick
def high_tail(high,open,close):
    return high - max([open,close])

def low_tail(low,open,close):
    return min([open,close])-low

def candle_no_head(open,high,low,close, percent=0.01):
    high_t = high_tail(high,open,close)
    height = candle_height(high,low)
    if height == 0:
        return False
    return high_t/height < percent

def candle_no_tail(open,high,low,close, percent=0.01):
    low_t = low_tail(low,open,close)
    height = candle_height(high,low)
    if height == 0:
        return False
    return low_t/height < percent

def candle_height(high,low):
    return high - low
# Define a function to calculate the height of a candlestick

def is_bulllish(open,close):
    return close > open
# Define a function to check if a candlestick is bullish
def is_bearish(open,close):
    return close < open 

def check_candle_notail_bullish(open,high,low,close):
    return is_bulllish(open,close) and candle_no_tail(open,high,low,close) 
# Define a function to check if a candlestick is bullish with no head
def check_candle_nohead_bearish(open,high,low,close):
    return is_bearish(open,close) and candle_no_head(open,high,low,close)

def above_body(high,open,close):
    return high - min([open,close])
# Define a function to check if a candlestick is above its body
def below_body(low,open,close):
    return max([open,close]) - low

def check_candle_notail_bullish_with_long_body(open,high,low,close,percent: float=0.5):
    # Define a function to check if a candlestick has no head and a long body
    above_bd = real_body(open,close)
    height = candle_height(high,low)
    if height == 0:
        return False
    return check_candle_notail_bullish(open,high,low,close) and above_bd/height >= percent

def check_candle_nohead_bearish_with_long_body(open,high,low,close,percent: float=0.5):
    # Define a function to check if a candlestick has no tail and a long body
    below_bd = real_body(open,close)
    height = candle_height(high,low)
    if height == 0:
        return False
    return check_candle_nohead_bearish(open,high,low,close) and is_bearish(open,close) and below_bd/height >= percent