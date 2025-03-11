from concurrent.futures import Future
import pandas as pd
import numpy as np
from atklip.appmanager.worker.return_worker import HeavyProcess
import atklip.controls as ta

def candle_pattern(df:pd.DataFrame,C_Len: int= 14,C_ShadowPercent:float = 5.0):
    """_summary_
    // Created by Robert N. 030715
    // Updated 031115
    // Candle labels
    study(title = "Candles", overlay = true)

    DojiSize = input(0.05, minval=0.01, title="Doji size")
    data=(abs(open - close) <= (high - low) * DojiSize)
    plotchar(data, title="Doji", text='Doji', color=white)

    data2=(close[2] > open[2] and min(open[1], close[1]) > close[2] and open < min(open[1], close[1]) and close < open )
    plotshape(data2, title= "Evening Star", color=red, style=shape.arrowdown, text="Evening\nStar")

    data3=(close[2] < open[2] and max(open[1], close[1]) < close[2] and open > max(open[1], close[1]) and close > open )
    plotshape(data3,  title= "Morning Star", location=location.belowbar, color=lime, style=shape.arrowup, text="Morning\nStar")

    data4=(open[1] < close[1] and open > close[1] and high - max(open, close) >= abs(open - close) * 3 and min(close, open) - low <= abs(open - close))
    plotshape(data4, title= "Shooting Star", color=red, style=shape.arrowdown, text="Shooting\nStar")

    data5=(((high - low)>3*(open -close)) and  ((close - low)/(.001 + high - low) > 0.6) and ((open - low)/(.001 + high - low) > 0.6))
    plotshape(data5, title= "Hammer", location=location.belowbar, color=white, style=shape.diamond, text="H")

    data5b=(((high - low)>3*(open -close)) and  ((high - close)/(.001 + high - low) > 0.6) and ((high - open)/(.001 + high - low) > 0.6))
    plotshape(data5b, title= "Inverted Hammer", location=location.belowbar, color=white, style=shape.diamond, text="IH")


    data6=(close[1] > open[1] and open > close and open <= close[1] and open[1] <= close and open - close < close[1] - open[1] )
    plotshape(data6, title= "Bearish Harami",  color=red, style=shape.arrowdown, text="Bearish\nHarami")

    data7=(open[1] > close[1] and close > open and close <= open[1] and close[1] <= open and close - open < open[1] - close[1] )
    plotshape(data7,  title= "Bullish Harami", location=location.belowbar, color=lime, style=shape.arrowup, text="Bullish\nHarami")

    data8=(close[1] > open[1] and open > close and open >= close[1] and open[1] >= close and open - close > close[1] - open[1] )
    plotshape(data8,  title= "Bearish Engulfing", color=red, style=shape.arrowdown, text="Bearish\nEngulfing")

    data9=(open[1] > close[1] and close > open and close >= open[1] and close[1] >= open and close - open > open[1] - close[1] )
    plotshape(data9, title= "Bullish Engulfing", location=location.belowbar, color=lime, style=shape.arrowup, text="Bullish\nEngulfling")

    upper = highest(10)[1]
    data10=(close[1] < open[1] and  open < low[1] and close > close[1] + ((open[1] - close[1])/2) and close < open[1])
    plotshape(data10, title= "Piercing Line", location=location.belowbar, color=lime, style=shape.arrowup, text="Piercing\nLine")

    lower = lowest(10)[1]
    data11=(low == open and  open < lower and open < close and close > ((high[1] - low[1]) / 2) + low[1])
    plotshape(data11, title= "Bullish Belt", location=location.belowbar, color=lime, style=shape.arrowup, text="Bullish\nBelt")

    data12=(open[1]>close[1] and open>=open[1] and close>open)
    plotshape(data12, title= "Bullish Kicker", location=location.belowbar, color=lime, style=shape.arrowup, text="Bullish\nKicker")

    data13=(open[1]<close[1] and open<=open[1] and close<=open)
    plotshape(data13, title= "Bearish Kicker", color=red, style=shape.arrowdown, text="Bearish\nKicker")

    data14=(((high-low>4*(open-close))and((close-low)/(.001+high-low)>=0.75)and((open-low)/(.001+high-low)>=0.75)) and high[1] < open and high[2] < open)
    plotshape(data14,  title= "Hanging Man", color=red, style=shape.arrowdown, text="Hanging\nMan")

    data15=((close[1]>open[1])and(((close[1]+open[1])/2)>close)and(open>close)and(open>close[1])and(close>open[1])and((open-close)/(.001+(high-low))>0.6))
    plotshape(data15, title= "Dark Cloud Cover", color=red, style=shape.arrowdown, text="Dark\nCloudCover")


    Args:
        df (pd.DataFrame): _description_
        doji_size (float, optional): _description_. Defaults to 0.05.

    Returns:
        _type_: _description_
    """
    output_df = pd.DataFrame([])
    df = df.copy()
    output_df["index"] = df["index"]
    
    df['C_BodyHi'] = np.maximum(df['close'], df['open'])
    df['C_BodyLo'] = np.minimum(df['close'], df['open'])
    df['C_Body'] = df['C_BodyHi'] - df['C_BodyLo']
    
    # # Average Body Size
    # df['C_BodyAvg'] = ta.ema(df['C_Body'], length=C_Len)
    # df['C_SmallBody'] = df['C_Body'] < df['C_BodyAvg']
    # df['C_LongBody'] = df['C_Body'] > df['C_BodyAvg']
    
    # Shadow Calculations
    df['C_UpShadow'] = df['high'] - df['C_BodyHi']
    df['C_DnShadow'] = df['C_BodyLo'] - df['low']
    df['C_HasUpShadow'] = df['C_UpShadow'] > (C_ShadowPercent / 100) * df['C_Body']
    df['C_HasDnShadow'] = df['C_DnShadow'] > (C_ShadowPercent / 100) * df['C_Body']
    
    # Body Characteristics
    df['C_WhiteBody'] = df['open'] < df['close']
    df['C_BlackBody'] = df['open'] > df['close']
    df['C_Range'] = df['high'] - df['low']
    df['C_LongBody_23'] = df['C_Body'] > (2 / 3) * df['C_Range']
    df['C_LongBody_12'] = df['C_Body'] > (1 / 2) * df['C_Range']
    
    # df['doji'] = (abs(df['open'] - df['close']) <= (df['high'] - df['low']) * doji_size)
    #MichaelHarris
    # Buy condition
    output_df['bullish_engulfing'] = (df['C_WhiteBody'])&\
                                    (df['C_LongBody_23'])&\
                                    (df['C_BlackBody'].shift(1))&\
                                    (df['C_LongBody_12'].shift(1))&\
                                    (df['C_BlackBody'].shift(2))&\
                                    (df['C_LongBody_12'].shift(2))&\
                                    (df['high'].shift(1) < df['high']) & (df['high']< df['high'].shift(2))&\
                                    (df['close'] > df['high'].shift(1))&\
                                    (df['low'] < df['low'].shift(1))&\
                                    (df['low'].shift(2) > df['close'].shift(1))&\
                                    (df['high'].shift(1) < df['open'].shift(2))&\
                                    (df['close'].shift(2)< df['high'].shift(1)) & (df['low'].shift(2)< df['close'].shift(1))

    output_df["buy_harris"] = (df['high'] > df['high'].shift(1))&\
                                (df['high'].shift(1) > df['low'])&\
                                (df['low'] > df['high'].shift(2))&\
                                (df['high'].shift(2) > df['low'].shift(1))&\
                                (df['low'].shift(1) > df['high'].shift(3))&\
                                (df['high'].shift(3) > df['low'].shift(2))&\
                                (df['low'].shift(2) > df['low'].shift(3))
                            
    # Symmetrical conditions for short (sell condition)
    output_df["sell_harris"] = (df['low'] < df['low'].shift(1))&\
                                (df['low'].shift(1) < df['high'])&\
                                (df['high'] < df['low'].shift(2))&\
                                (df['low'].shift(2) < df['high'].shift(1))&\
                                (df['high'].shift(1) < df['low'].shift(3))&\
                                (df['low'].shift(3) < df['high'].shift(2))&\
                                (df['high'].shift(2) < df['high'].shift(3))
    

    output_df["buy_simple"] = (df['C_BlackBody'])&\
                            (df['high'] > df['high'].shift(1))&\
                            (df['low'] < df['low'].shift(1))&\
                            (df['close'] < df['low'].shift(1))

    output_df["sell_simple"] = (df['C_WhiteBody'])&\
                                (df['low'] < df['low'].shift(1))&\
                                (df['high'] > df['high'].shift(1))&\
                                (df['close'] > df['high'].shift(1))

    # output_df['evening_star'] = (df['close'].shift(2) > df['open'].shift(2)) & \
    #                     (np.minimum(df['open'].shift(1), df['close'].shift(1)) > df['close'].shift(2)) & \
    #                     (df['open'] < np.minimum(df['open'].shift(1), df['close'].shift(1))) & \
    #                     (df['close'] < df['open'])
    # "data3=(close[2] < open[2] and max(open[1], close[1]) < close[2] and open > max(open[1], close[1]) and close > open )"
    # output_df['morning_star'] = (df['close'].shift(2) < df['open'].shift(2)) & \
    #                     (np.maximum(df['open'].shift(1), df['close'].shift(1)) < df['close'].shift(2)) & \
    #                     (df['open'] > np.maximum(df['open'].shift(1), df['close'].shift(1))) & \
    #                     (df['close'] > df['open'])
    # "data4=(open[1] < close[1] and open > close[1] and high - max(open, close) >= abs(open - close) * 3 and min(close, open) - low <= abs(open - close))"
    # output_df['shooting_star'] = (df['open'].shift(1) < df['close'].shift(1)) & \
    #                     (df['open'] > df['close'].shift(1)) & \
    #                     ((df['high'] - np.maximum(df['open'], df['close'])) >= abs(df['open'] - df['close']) * 3) & \
    #                     ((np.minimum(df['close'], df['open']) - df['low']) <= abs(df['open'] - df['close']))

    # df['hammer'] = ((df['high'] - df['low']) > 3 * abs(df['open'] - df['close'])) & \
    #             (((df['close'] - df['low']) / (0.001 + df['high'] - df['low'])) > 0.6) & \
    #             (((df['open'] - df['low']) / (0.001 + df['high'] - df['low'])) > 0.6)

    # df['inverted_hammer'] = ((df['high'] - df['low']) > 3 * abs(df['open'] - df['close'])) & \
    #                         (((df['high'] - df['close']) / (0.001 + df['high'] - df['low'])) > 0.6) & \
    #                         (((df['high'] - df['open']) / (0.001 + df['high'] - df['low'])) > 0.6)
    # "data6=(close[1] > open[1] and open > close and open <= close[1] and open[1] <= close and open - close < close[1] - open[1] )"
    # output_df['bearish_harami'] = (df['close'].shift(1) > df['open'].shift(1)) & \
    #                     (df['open'] > df['close']) & \
    #                     (df['open'] <= df['close'].shift(1)) & \
    #                     (df['open'].shift(1) <= df['close']) & \
    #                     (abs(df['open'] - df['close']) < abs(df['close'].shift(1) - df['open'].shift(1)))
    # "data7=(open[1] > close[1] and close > open and close <= open[1] and close[1] <= open and close - open < open[1] - close[1] )"
    # output_df['bullish_harami'] = (df['open'].shift(1) > df['close'].shift(1)) & \
    #                     (df['close'] > df['open']) & \
    #                     (df['close'] <= df['open'].shift(1)) & \
    #                     (df['close'].shift(1) <= df['open']) & \
    #                     (abs(df['close'] - df['open']) < abs(df['open'].shift(1) - df['close'].shift(1)))
    # "data8=(close[1] > open[1] and open > close and open >= close[1] and open[1] >= close and open - close > close[1] - open[1] )"
    # output_df['bearish_engulfing'] = (df['close'].shift(1) > df['open'].shift(1)) & \
    #                         (df['open'] > df['close']) & \
    #                         (df['open'] >= df['close'].shift(1)) & \
    #                         (df['close'] <= df['open'].shift(1)) & \
    #                         (abs(df['open'] - df['close']) > abs(df['close'].shift(1) - df['open'].shift(1)))
    # "data9=(open[1] > close[1] and close > open and close >= open[1] and close[1] >= open and close - open > open[1] - close[1] )"
    # output_df['bullish_engulfing'] = (df['open'].shift(1) > df['close'].shift(1)) & \
    #                         (df['close'] > df['open']) & \
    #                         (df['close'] >= df['open'].shift(1)) & \
    #                         (df['open'] <= df['close'].shift(1)) & \
    #                         (abs(df['close'] - df['open']) > abs(df['open'].shift(1) - df['close'].shift(1)))
    # df['piercing_line'] = (df['close'].shift(1) < df['open'].shift(1)) & \
    #                     (df['open'] < df['low'].shift(1)) & \
    #                     (df['close'] > (df['close'].shift(1) + (df['open'].shift(1) - df['close'].shift(1)) / 2)) & \
    #                     (df['close'] < df['open'].shift(1))

    # df['bullish_belt'] = (df['low'] == df['open']) & \
    #                     (df['open'] < df['low'].rolling(10).min().shift(1)) & \
    #                     (df['close'] > ((df['high'].shift(1) - df['low'].shift(1)) / 2) + df['low'].shift(1))

    # output_df['bullish_kicker'] = (df['open'].shift(1) > df['close'].shift(1)) & \
    #                     (df['open'] >= df['open'].shift(1)) & \
    #                     (df['close'] > df['open'])

    # output_df['bearish_kicker'] = (df['open'].shift(1) < df['close'].shift(1)) & \
    #                     (df['open'] <= df['open'].shift(1)) & \
    #                     (df['close'] <= df['open'])
    # df['hanging_man'] = ((df['high'] - df['low']) > 4 * abs(df['open'] - df['close'])) & \
    #                     (((df['close'] - df['low']) / (0.001 + df['high'] - df['low'])) >= 0.75) & \
    #                     (((df['open'] - df['low']) / (0.001 + df['high'] - df['low'])) >= 0.75) & \
    #                     (df['high'].shift(1) < df['open']) & \
    #                     (df['high'].shift(2) < df['open'])

    # df['dark_cloud_cover'] = (df['close'].shift(1) > df['open'].shift(1)) & \
    #                         (((df['close'].shift(1) + df['open'].shift(1)) / 2) > df['close']) & \
    #                         (df['open'] > df['close']) & \
    #                         (df['open'] > df['close'].shift(1)) & \
    #                         (df['close'] > df['open'].shift(1)) & \
    #                         ((df['open'] - df['close']) / (0.001 + (df['high'] - df['low'])) > 0.6)
    return output_df
# # Các mẫu nến khác có thể được bổ sung tương tự theo mã Pine Script gốc.


def identify_patterns(df:pd.DataFrame):
    """
    Hàm nhận diện các mẫu nến từ dữ liệu OHLC.
    Args:
        df (pd.DataFrame): DataFrame chứa dữ liệu OHLC với các cột ['open', 'high', 'low', 'close'].
    _summary_
        Check for Bearish Engulfing pattern
       if((C1 > O1) & (O > C) & (O >= C1) & (O1 >= C) & ((O - C) > (C1 - O1))) 
       
        // Check for a Three Outside Down pattern
       if((C2 > O2) & (O1 > C1) & (O1 >= C2) & (O2 >= C1) & ((O1 - C1) > (C2 - O2)) & (O > C) & (C < C1)) 
        
        // Check for a Dark Cloud Cover pattern
       if((C1 > O1) & (((C1 + O1) / 2) > C) & (O > C) & (O > C1) & (C > O1) & ((O - C) / (0.001 + (H - L)) > 0.6)) 
        
        // Check for Evening Doji Star pattern
       if((C2 > O2) & ((C2 - O2) / (0.001 + H2 - L2) > 0.6) & (C2 < O1) & (C1 > O1) & ((H1-L1) > (3*(C1 - O1))) & (O > C) & (O < O1)) 
        
        // Check for Bearish Harami pattern
       if((C1 > O1) & (O > C) & (O <= C1) & (O1 <= C) & ((O - C) < (C1 - O1))) 
       
       // Check for Three Inside Down pattern
       if((C2 > O2) & (O1 > C1) & (O1 <= C2) & (O2 <= C1) & ((O1 - C1) < (C2 - O2)) & (O > C) & (C < C1) & (O < O1)) 
        
        // Check for Three Black Crows pattern
       if((O > C*1.01) & (O1 > C1*1.01) & (O2 > C2*1.01) & (C < C1) & (C1 < C2) & (O > C1) & (O < O1) & (O1 > C2) & (O1 < O2) & (((C - L) / (H - L)) < 0.2) & (((C1 - L1) / (H1 - L1)) < 0.2) & (((C2 - L2) / (H2 - L2)) < 0.2))
        
        //Check for Evening Star Pattern
       if((C2 > O2) & ((C2 - O2) / (0.001 + H2 - L2) > 0.6) & (C2 < O1) & (C1 > O1) & ((H1 - L1) > (3*(C1 - O1))) & (O > C) & (O < O1)) 
    
    
    // Bullish Patterns
       // Check for Bullish Engulfing pattern
       if((O1 > C1) & (C > O) & (C >= O1) & (C1 >= O) & ((C - O) > (O1 - C1))) 
    // Check for Three Outside Up pattern
       if((O2 > C2) & (C1 > O1) & (C1 >= O2) & (C2 >= O1) & ((C1 - O1) > (O2 - C2)) & (C > O) & (C > C1)) 
    // Check for Bullish Harami pattern
       if((O1 > C1) & (C > O) & (C <= O1) & (C1 <= O) & ((C - O) < (O1 - C1))) 
    
    // Check for Three Inside Up pattern
       if((O2 > C2) & (C1 > O1) & (C1 <= O2) & (C2 <= O1) & ((C1 - O1) < (O2 - C2)) & (C > O) & (C > C1) & (O > O1)) 
    // Check for Piercing Line pattern
       if((C1 < O1) & (((O1 + C1) / 2) < C) & (O < C) & (O < C1) & (C < O1) & ((C - O) / (0.001 + (H - L)) > 0.6)) 
    // Check for Three White Soldiers pattern
       if((C > O*1.01) & (C1 > O1*1.01) & (C2 > O2*1.01) & (C > C1) & (C1 > C2) & 
          (O < C1) & (O > O1) & (O1 < C2) & (O1 > O2) & (((H - C) / (H - L)) < 0.2) & 
          (((H1 - C1) / (H1 - L1)) < 0.2) & (((H2 - C2) / (H2 - L2)) < 0.2)) 
    // Check for Morning Doji Star
       if((O2 > C2) & ((O2 - C2) / (0.001 + H2 - L2) > 0.6) & (C2 > O1) & (O1 > C1) & 
          ((H1 - L1) > (3*(C1 - O1))) & (C > O) & (O > O1)) 

    Returns:
        pd.DataFrame: DataFrame với các cột bổ sung cho mỗi mẫu nến được nhận diện.
    """
    # Tạo cột Range trung bình cho mỗi 10 cây nến
    # df['range'] = (df['high'] - df['low']).rolling(window=10).mean()
    df = df.copy()
    # Khởi tạo các cột mẫu nến
    patterns = ["index",
        'bearish_engulfing', 'three_outside_down', 'dark_cloud_cover',"bearish_ziad_francis",
        'evening_doji_star', 'bearish_harami', 'three_inside_down',"evenning_star",
        'three_black_crows', #"sell_simple",
        'bullish_engulfing',#"buy_simple",
        'three_outside_up', 'bullish_harami', 'three_inside_up',"bull_ziad_francis",
        'piercing_line', 'three_white_soldiers', 'morning_doji_star'
    ]

    # Lấy giá Open, High, Low, Close cho các cột trước đó
    O, H, L, C = df['open'], df['high'], df['low'], df['close']
    O1, H1, L1, C1 = O.shift(1), H.shift(1), L.shift(1), C.shift(1)
    O2, H2, L2, C2 = O.shift(2), H.shift(2), L.shift(2), C.shift(2)

    # Bearish Patterns
    df['bearish_engulfing'] = (C1 > O1) & (O > C) & (O >= C1) & (O1 >= C) & ((O - C) > (C1 - O1))
    df['three_outside_down'] = (C2 > O2) & (O1 > C1) & (O1 >= C2) & (O2 >= C1) & ((O1 - C1) > (C2 - O2)) & (O > C) & (C < C1)
    df['dark_cloud_cover'] = (C1 > O1) & (((C1 + O1) / 2) > C) & (O > C) & (O > C1) & (C > O1) & ((O - C) / (0.001 + (H - L)) > 0.6)
    df['evening_doji_star'] = (C2 > O2) & ((C2 - O2) / (0.001 + H2 - L2) > 0.6) & (C2 < O1) & (C1 > O1) & ((H1-L1) > (3*(C1 - O1))) & (O > C) & (O < O1)
    df['bearish_harami'] = (C1 > O1) & (O > C) & (O <= C1) & (O1 <= C) & ((O - C) < (C1 - O1))
    df['three_inside_down'] = (C2 > O2) & (O1 > C1) & (O1 <= C2) & (O2 <= C1) & ((O1 - C1) < (C2 - O2)) & (O > C) & (C < C1) & (O < O1)
    df['three_black_crows'] = (O > C*1.01) & (O1 > C1*1.01) & (O2 > C2*1.01) & (C < C1) & (C1 < C2) & (O > C1) & (O < O1) & (O1 > C2) & (O1 < O2) & (((C - L) / (H - L)) < 0.2) & (((C1 - L1) / (H1 - L1)) < 0.2) & (((C2 - L2) / (H2 - L2)) < 0.2)
    df["evenning_star"] = (C2 > O2) & ((C2 - O2) / (0.001 + H2 - L2) > 0.6) & (C2 < O1) & (C1 > O1) & ((H1 - L1) > (3*(C1 - O1))) & (O > C) & (O < O1)
    
    # df["sell_simple"] = (O<C)&(L < L1)&(H > H1)&(C > H1)
    "https://www.youtube.com/watch?v=tOH6Bd_jvfA&ab_channel=CodeTrading"
    df["bearish_ziad_francis"] = (L<C) & (C<L2) & (L2<L1) & (L1<H) & (H<H2) & (H2<H1)

    
    # Bullish Patterns
    df['bullish_engulfing'] = (O1 > C1) & (C > O) & (C >= O1) & (C1 >= O) & ((C - O) > (O1 - C1))
    df['three_outside_up'] = (O2 > C2) & (C1 > O1) & (C1 >= O2) & (C2 >= O1) & ((C1 - O1) > (O2 - C2)) & (C > O) & (C > C1)
    df['bullish_harami'] = (O1 > C1) & (C > O) & (C <= O1) & (C1 <= O) & ((C - O) < (O1 - C1))
    df['three_inside_up'] = (O2 > C2) & (C1 > O1) & (C1 <= O2) & (C2 <= O1) & ((C1 - O1) < (O2 - C2)) & (C > O) & (C > C1) & (O > O1)
    df['piercing_line'] = (C1 < O1) & (((O1 + C1) / 2) < C) & (O < C) & (O < C1) & (C < O1) & ((C - O) / (0.001 + (H - L)) > 0.6)
    df['three_white_soldiers'] = (C > O*1.01) & (C1 > O1*1.01) & (C2 > O2*1.01) & (C > C1) & (C1 > C2) & (O < C1) & (O > O1) & (O1 < C2) & (O1 > O2) & (((H - C) / (H - L)) < 0.2) & (((H1 - C1) / (H1 - L1)) < 0.2) & (((H2 - C2) / (H2 - L2)) < 0.2)
    df['morning_doji_star'] = (O2 > C2) & ((O2 - C2) / (0.001 + H2 - L2) > 0.6) & (C2 > O1) & (O1 > C1) & ((H1 - L1) > (3*(C1 - O1))) & (C > O) & (O > O1)

    # df["buy_simple"] = (O>C)&(H > H1)&(L < L1)&(C < L1)
    df["bull_ziad_francis"] = (H>C) & (C>H2) & (H2>H1) & (H1>L) & (L>L2) & (L2>L1)
    

    return df[patterns]





import numpy as np
import pandas as pd
from typing import List
from atklip.controls.ohlcv import   OHLCV
from atklip.controls.candle import JAPAN_CANDLE,HEIKINASHI,SMOOTH_CANDLE,N_SMOOTH_CANDLE
from atklip.appmanager import ThreadPoolExecutor_global as ApiThreadPool
from PySide6.QtCore import Signal,QObject

class AllCandlePattern(QObject):
    sig_update_candle = Signal()
    sig_add_candle = Signal()
    sig_reset_all = Signal()
    signal_delete = Signal()    
    sig_add_historic = Signal(int) 
    def __init__(self,_candles,dict_ta_params:dict={}) -> None:
        super().__init__(parent=None)
        self._candles: JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE =_candles
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        self.is_histocric_load = False
        self._name = f"ALL CDL PATTERN"

        self.df = pd.DataFrame([])
        self.worker = ApiThreadPool

        self.connect_signals()
    @property
    def is_current_update(self)-> bool:
        return self._is_current_update
    @is_current_update.setter
    def is_current_update(self,_is_current_update):
        self._is_current_update = _is_current_update
    @property
    def source_name(self)-> str:
        return self._source_name
    @source_name.setter
    def source_name(self,source_name):
        self._source_name = source_name
    
    def change_input(self,candles=None,dict_ta_params: dict={}):
        if candles != None:
            self.disconnect_signals()
            self._candles : JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE= candles
            self.connect_signals()
        
        self.first_gen = False
        self.is_genering = True
        self.is_current_update = False
        
        self.fisrt_gen_data()
    
    def disconnect_signals(self):
        try:
            self._candles.sig_reset_all.disconnect(self.started_worker)
            self._candles.sig_update_candle.disconnect(self.update_worker)
            self._candles.sig_add_candle.disconnect(self.add_worker)
            self._candles.signal_delete.disconnect(self.signal_delete)
            self._candles.sig_add_historic.disconnect(self.add_historic_worker)
        except RuntimeError:
                    pass
    
    def connect_signals(self):
        self._candles.sig_reset_all.connect(self.started_worker)
        self._candles.sig_update_candle.connect(self.update_worker)
        self._candles.sig_add_candle.connect(self.add_worker)
        self._candles.signal_delete.connect(self.signal_delete)
        self._candles.sig_add_historic.connect(self.add_historic_worker)
    
    
    def change_source(self,_candles:JAPAN_CANDLE|HEIKINASHI|SMOOTH_CANDLE|N_SMOOTH_CANDLE):
        self.disconnect_signals()
        self._candles =_candles
        self.connect_signals()
        self.started_worker()
    
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self,_name):
        self._name = _name
    
    def get_df(self,n:int=None):
        if not n:
            return self.df
        return self.df.tail(n)
    
    
    def get_data(self,start:int=0,stop:int=0):
        if len(self.df) == 0:
            return []
        if start == 0 and stop == 0:
            df=self.df
        elif start == 0 and stop != 0:
            df=self.df.iloc[:stop]
        elif start != 0 and stop == 0:
            df=self.df.iloc[start:]
        else:
            df=self.df.iloc[start:stop]
        return df
    
    def get_last_row_df(self):
        return self.df.iloc[-1] 

    def update_worker(self,candle):
        self.worker.submit(self.update,candle)

    def add_worker(self,candle):
        self.worker.submit(self.add,candle)
    
    def add_historic_worker(self,n):
        self.worker.submit(self.add_historic,n)

    def started_worker(self):
        self.worker.submit(self.fisrt_gen_data)
    
    def paire_data(self,INDICATOR:pd.DataFrame|pd.Series):
        return
    
    
    @staticmethod
    def calculate(df: pd.DataFrame):
        df = df.copy()
        df = df.reset_index(drop=True)
        INDICATOR = identify_patterns(df)
        return INDICATOR
        
    def fisrt_gen_data(self):
        self.is_current_update = False
        self.is_genering = True
        self.df = pd.DataFrame([])
        df:pd.DataFrame = self._candles.get_df()
        process = HeavyProcess(self.calculate,
                               self.callback_first_gen,
                               df)
        process.start()
        
    
    def add_historic(self,n:int):
        self.is_genering = True
        self.is_histocric_load = False
        _pre_len = len(self.df)
        candle_df = self._candles.get_df()
        df:pd.DataFrame = candle_df.head(-_pre_len)
        
        process = HeavyProcess(self.calculate,
                               self.callback_gen_historic_data,
                               df)
        process.start()
       
    def add(self,new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(10)
            process = HeavyProcess(self.calculate,
                               self.callback_add,
                               df)
            process.start()
        else:
            pass
            #self.is_current_update = True
            
    def update(self, new_candles:List[OHLCV]):
        new_candle:OHLCV = new_candles[-1]
        self.is_current_update = False
        if (self.first_gen == True) and (self.is_genering == False):
            df:pd.DataFrame = self._candles.get_df(10)
            process = HeavyProcess(self.calculate,
                               self.callback_update,
                               df)
            process.start() 
        else:
            pass
            #self.is_current_update = True
    
    def callback_first_gen(self, future: Future):
        self.df = future.result()
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        #self.is_current_update = True
        self.sig_reset_all.emit()
    
    def callback_gen_historic_data(self, future: Future):
        _df = future.result()
        _len = len(_df)
        self.df = pd.concat([_df,self.df],ignore_index=True)
        self.is_genering = False
        if self.first_gen == False:
            self.first_gen = True
            self.is_genering = False
        self.is_histocric_load = True
        self.sig_add_historic.emit(_len)
           
    def callback_add(self,future: Future):
        _df = future.result()
        _new_df = _df.iloc[[-1]]
        self.df = pd.concat([self.df,_new_df],ignore_index=True)
        self.sig_add_candle.emit()
        #self.is_current_update = True
  
    def callback_update(self,future: Future):
        _df = future.result()
        self.df.iloc[-1] = _df.iloc[-1]
        self.sig_update_candle.emit()
        #self.is_current_update = True