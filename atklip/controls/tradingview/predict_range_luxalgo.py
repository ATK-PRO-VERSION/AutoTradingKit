import numpy as np
import pandas as pd
import pandas_ta as ta

# Hàm tính toán Predictive Ranges (giống như trong Pine Script)
def pred_ranges(df, length, mult):
    # Tính toán ATR (Average True Range)
    atr = ta.atr(df['high'], df['low'], df['close'], length)
    
    # Tính toán giá trị trung bình (avg)
    avg = df['close']
    
    # Tính toán các mức giá dự đoán
    hold_atr = np.zeros(len(df))
    
    prR2 = np.zeros(len(df))
    prR1 = np.zeros(len(df))
    prS1 = np.zeros(len(df))
    prS2 = np.zeros(len(df))
    
    for i in range(1, len(df)):
        atr_val = atr[i] * mult
        
        # Điều chỉnh avg sao cho nó không vượt quá biên ATR
        if df['close'][i] - avg[i-1] > atr_val:
            avg[i] = avg[i-1] + atr_val
        elif avg[i-1] - df['close'][i] > atr_val:
            avg[i] = avg[i-1] - atr_val
        else:
            avg[i] = avg[i-1]
        
        # Tính toán hold_atr
        if avg[i] != avg[i-1]:
            hold_atr[i] = atr[i] / 2
        else:
            hold_atr[i] = hold_atr[i-1]
        
        # Tính các mức giá dự đoán
        prR2[i] = avg[i] + hold_atr[i] * 2
        prR1[i] = avg[i] + hold_atr[i]
        prS1[i] = avg[i] - hold_atr[i]
        prS2[i] = avg[i] - hold_atr[i] * 2
    
    return prR2, prR1, avg, prS1, prS2

# Giả sử bạn có dữ liệu trong một DataFrame pandas với các cột 'high', 'low', 'close'
# Ví dụ dữ liệu:
data = {
    'high': [100, 105, 102, 107, 110],
    'low': [95, 100, 98, 103, 106],
    'close': [98, 102, 100, 105, 109]
}
df = pd.DataFrame(data)

# Các tham số
length = 200
mult = 6.0

# Tính toán các mức dự đoán
prR2, prR1, avg, prS1, prS2 = pred_ranges(df, length, mult)

# In kết quả (có thể trả về dưới dạng DataFrame nếu muốn)
result = pd.DataFrame({
    'prR2': prR2,
    'prR1': prR1,
    'avg': avg,
    'prS1': prS1,
    'prS2': prS2
})

print(result)