import numpy as np
import pandas as pd
import pandas_ta as ta
import math

def calculate_OTT(df, src='close', length=2, percent=1.4, mav='VAR'):
    df = df.copy()
    
    # Calculate selected moving average
    if mav == 'SMA':
        df['MAvg'] = df[src].rolling(window=length).mean()
    elif mav == 'EMA':
        df['MAvg'] = df[src].ewm(span=length, adjust=False).mean()
    elif mav == 'WMA':
        df['MAvg'] = ta.wma(df[src], length=length)
    elif mav == 'TMA':
        ceil_half = math.ceil(length / 2)
        floor_half_plus1 = math.floor(length / 2) + 1
        sma1 = df[src].rolling(window=ceil_half).mean()
        df['MAvg'] = sma1.rolling(window=floor_half_plus1).mean()
    elif mav == 'VAR':
        vud1 = np.where(df[src] > df[src].shift(1), df[src] - df[src].shift(1), 0)
        vdd1 = np.where(df[src] < df[src].shift(1), df[src].shift(1) - df[src], 0)
        
        vUD = pd.Series(vud1).rolling(window=9).sum()
        vDD = pd.Series(vdd1).rolling(window=9).sum()
        
        vCMO = (vUD - vDD) / (vUD + vDD).replace(0, np.nan)
        vCMO = vCMO.fillna(0)
        valpha = 2 / (length + 1)
        
        VAR = np.zeros(len(df))
        for i in range(len(df)):
            if i == 0:
                VAR[i] = valpha * abs(vCMO.iloc[i]) * df[src].iloc[i]
            else:
                prev_VAR = VAR[i-1] if not np.isnan(VAR[i-1]) else 0
                VAR[i] = valpha * abs(vCMO.iloc[i]) * df[src].iloc[i] + (1 - valpha * abs(vCMO.iloc[i])) * prev_VAR
        df['MAvg'] = VAR
    elif mav == 'WWMA':
        alpha = 1 / length
        WWMA = np.zeros(len(df))
        for i in range(len(df)):
            if i == 0:
                WWMA[i] = alpha * df[src].iloc[i]
            else:
                prev_WWMA = WWMA[i-1] if not np.isnan(WWMA[i-1]) else 0
                WWMA[i] = alpha * df[src].iloc[i] + (1 - alpha) * prev_WWMA
        df['MAvg'] = WWMA
    elif mav == 'ZLEMA':
        zxLag = (length // 2) if (length % 2 == 0) else ((length - 1) // 2)
        zxEMAData = df[src] + (df[src] - df[src].shift(zxLag))
        df['MAvg'] = zxEMAData.ewm(span=length, adjust=False).mean()
    elif mav == 'TSF':
        df['lrc'] = ta.linreg(df[src], length=length)
        df['lrc1'] = df['lrc'].shift(1)
        df['lrs'] = df['lrc'] - df['lrc1']
        df['MAvg'] = df['lrc'] + df['lrs']
    else:
        raise ValueError(f"Invalid MAV type: {mav}")
    
    # Calculate OTT
    df['fark'] = df['MAvg'] * percent * 0.01
    
    longStop = np.zeros(len(df))
    shortStop = np.zeros(len(df))
    dir_arr = np.ones(len(df))
    
    for i in range(len(df)):
        if i == 0:
            longStop[i] = df['MAvg'].iloc[i] - df['fark'].iloc[i]
            shortStop[i] = df['MAvg'].iloc[i] + df['fark'].iloc[i]
        else:
            # Update longStop
            prev_long = longStop[i-1] if not np.isnan(longStop[i-1]) else longStop[i-1]
            current_ma = df['MAvg'].iloc[i]
            new_long = current_ma - df['fark'].iloc[i]
            
            if current_ma > prev_long:
                longStop[i] = max(new_long, prev_long)
            else:
                longStop[i] = new_long
            
            # Update shortStop
            prev_short = shortStop[i-1] if not np.isnan(shortStop[i-1]) else shortStop[i-1]
            new_short = current_ma + df['fark'].iloc[i]
            
            if current_ma < prev_short:
                shortStop[i] = min(new_short, prev_short)
            else:
                shortStop[i] = new_short
            
            # Update direction
            prev_dir = dir_arr[i-1]
            if prev_dir == -1 and current_ma > prev_short:
                dir_arr[i] = 1
            elif prev_dir == 1 and current_ma < prev_long:
                dir_arr[i] = -1
            else:
                dir_arr[i] = prev_dir
    
    df['MT'] = np.where(dir_arr == 1, longStop, shortStop)
    df['OTT'] = np.where(df['MAvg'] > df['MT'], 
                        df['MT'] * (200 + percent)/200, 
                        df['MT'] * (200 - percent)/200)
    
    # Shift OTT by 2 periods
    df['OTT'] = df['OTT'].shift(2)
    
    # Cleanup intermediate columns
    df.drop(['fark', 'MT', 'lrc', 'lrc1', 'lrs'], axis=1, errors='ignore', inplace=True)
    
    return df

# Example usage:
# Assuming df is a DataFrame with OHLC data
# df = calculate_OTT(df, mav='VAR', length=2, percent=1.4)