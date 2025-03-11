import pandas as pd
import numpy as np
import pandas_ta as ta

class SRLevel:
    def __init__(self, start_time, price, sr_type, timeframe, strength=1, ephemeral=False):
        self.start_time = start_time
        self.price = price
        self.sr_type = sr_type
        self.timeframe = timeframe
        self.strength = strength
        self.ephemeral = ephemeral
        self.break_time = None
        self.retest_times = []
        self.invalidated = False

    def __repr__(self):
        return f"{self.sr_type}@{self.price:.4f} ({self.timeframe})"

def calculate_sr_levels(df, pivot_length=15, atr_length=20, timeframe='', min_strength=1):
    sr_levels = []
    
    # Tính toán các chỉ báo
    df['pivot_high'] = df.ta.pivot_high(length=pivot_length)
    df['pivot_low'] = df.ta.pivot_low(length=pivot_length)
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=atr_length)
    df['avg_volume'] = df['volume'].rolling(atr_length).mean()
    
    # Tìm các điểm pivot và xác định SR
    for i in range(len(df)):
        if not np.isnan(df['pivot_high'].iloc[i]):
            price = df['pivot_high'].iloc[i]
            sr_type = 'Resistance'
            valid = True
            
            # Kiểm tra khoảng cách với các SR hiện có
            for sr in sr_levels:
                if abs(sr.price - price) < df['atr'].iloc[i] * 0.125:
                    valid = False
                    break
            
            if valid:
                sr_levels.append(SRLevel(
                    start_time=df.index[i],
                    price=price,
                    sr_type=sr_type,
                    timeframe=timeframe
                ))
        
        if not np.isnan(df['pivot_low'].iloc[i]):
            price = df['pivot_low'].iloc[i]
            sr_type = 'Support'
            valid = True
            
            for sr in sr_levels:
                if abs(sr.price - price) < df['atr'].iloc[i] * 0.125:
                    valid = False
                    break
            
            if valid:
                sr_levels.append(SRLevel(
                    start_time=df.index[i],
                    price=price,
                    sr_type=sr_type,
                    timeframe=timeframe
                ))
    
    return sr_levels

def process_timeframe(df, timeframe, config):
    # Resample data theo timeframe
    if timeframe != '':
        resampled = df.resample(timeframe).agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        })
    else:
        resampled = df.copy()
    
    # Tính toán SR levels cho timeframe này
    return calculate_sr_levels(
        resampled,
        pivot_length=config['pivot_length'],
        atr_length=config['atr_length'],
        timeframe=timeframe
    )

def merge_sr_levels(all_levels, atr, min_strength=1):
    merged = []
    
    # Lọc và hợp nhất các SR levels
    for level in all_levels:
        if level.strength < min_strength:
            continue
        
        exists = False
        for existing in merged:
            if (abs(existing.price - level.price) < atr * 0.125 and 
                existing.sr_type == level.sr_type):
                exists = True
                break
                
        if not exists:
            merged.append(level)
    
    return merged

def multi_timeframe_sr(df, config):
    all_levels = []
    
    # Xử lý từng timeframe
    for tf in config['timeframes']:
        if tf['enabled']:
            levels = process_timeframe(df, tf['value'], config)
            all_levels.extend(levels)
    
    # Tính toán ATR tổng hợp
    atr = ta.atr(df['high'], df['low'], df['close'], length=config['atr_length'])
    
    # Hợp nhất các SR levels
    return merge_sr_levels(
        all_levels,
        atr.mean(),
        min_strength=config['min_strength']
    )

# Cấu hình mẫu
config = {
    'pivot_length': 15,
    'atr_length': 20,
    'min_strength': 1,
    'timeframes': [
        {'enabled': True, 'value': ''},      # Khung thời gian gốc
        {'enabled': True, 'value': '4H'},    # 4 giờ
        {'enabled': False, 'value': 'D'},    # Ngày
    ]
}

# Sử dụng
if __name__ == "__main__":
    # Đọc dữ liệu mẫu
    df = pd.read_csv('data.csv', parse_dates=['date'], index_col='date')
    
    # Tính toán các mức SR
    sr_levels = multi_timeframe_sr(df, config)
    
    # In kết quả
    print("Support & Resistance Levels:")
    for level in sr_levels:
        print(f"- {level}")