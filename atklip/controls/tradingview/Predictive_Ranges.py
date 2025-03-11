import pandas as pd
import pandas_ta as ta

def compute_pred_ranges(df: pd.DataFrame, length: int, mult: float) -> tuple:
    """
    Tính toán các mức Predictive Ranges cho dữ liệu đã được resample
    """
    # Tính toán ATR và điền giá trị NaN bằng 0
    df['atr'] = ta.atr(df['high'], df['low'], df['close'], length=length) * mult
    df['atr'].fillna(0, inplace=True)
    
    # Khởi tạo các biến lưu trữ
    avg_values = []
    hold_atr_values = []
    
    # Giá trị ban đầu
    avg_prev = df['close'].iloc[0] if not df.empty else 0
    hold_atr_prev = 0.0
    
    avg_values.append(avg_prev)
    hold_atr_values.append(hold_atr_prev)
    
    # Duyệt qua từng hàng để tính toán các giá trị
    for i in range(1, len(df)):
        close = df['close'].iloc[i]
        atr = df['atr'].iloc[i]
        
        # Tính toán giá trị avg mới
        diff = close - avg_prev
        if diff > atr:
            new_avg = avg_prev + atr
        elif -diff > atr:
            new_avg = avg_prev - atr
        else:
            new_avg = avg_prev
        
        # Tính toán giá trị hold_atr
        if new_avg != avg_prev:
            hold_atr = atr / 2
        else:
            hold_atr = hold_atr_prev
        
        # Cập nhật giá trị previous
        avg_prev = new_avg
        hold_atr_prev = hold_atr
        
        # Lưu giá trị
        avg_values.append(new_avg)
        hold_atr_values.append(hold_atr)
    
    # Tính toán các mức giá
    prR2 = pd.Series(avg_values) + 2 * pd.Series(hold_atr_values)
    prR1 = pd.Series(avg_values) + pd.Series(hold_atr_values)
    avg = pd.Series(avg_values)
    prS1 = pd.Series(avg_values) - pd.Series(hold_atr_values)
    prS2 = pd.Series(avg_values) - 2 * pd.Series(hold_atr_values)
    
    return prR2, prR1, avg, prS1, prS2

def predictive_ranges(df: pd.DataFrame, length: int = 200, mult: float = 6.0, tf: str = 'D') -> pd.DataFrame:
    """
    Tính toán Predictive Ranges và merge kết quả vào DataFrame gốc
    """
    # Resample dữ liệu theo timeframe
    resampled = df.resample(tf).agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last'
    }).ffill()
    
    # Tính toán các mức trên dữ liệu đã resample
    prR2, prR1, avg, prS1, prS2 = compute_pred_ranges(resampled, length, mult)
    
    # Merge kết quả vào khung dữ liệu gốc
    for col, values in zip(['prR2', 'prR1', 'avg', 'prS1', 'prS2'], 
                          [prR2, prR1, avg, prS1, prS2]):
        df[col] = values.reindex(df.index, method='ffill')
    
    return df

# Ví dụ sử dụng
if __name__ == "__main__":
    # Đọc dữ liệu mẫu (cần thay thế bằng dữ liệu thực tế)
    data = pd.read_csv('data.csv', parse_dates=['date'], index_col='date')
    
    # Tính toán Predictive Ranges
    result = predictive_ranges(data, length=200, mult=6.0, tf='D')
    
    # Hiển thị kết quả
    print(result[['close', 'prR2', 'prR1', 'avg', 'prS1', 'prS2']].tail())