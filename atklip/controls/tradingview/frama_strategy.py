import numpy as np
import pandas as pd
import atklip.controls as ta

# Giả sử bạn đã có dữ liệu đóng mở, cao thấp dưới dạng DataFrame `df`
# Để dễ dàng hơn, bạn cần chuẩn bị một DataFrame có các cột: 'open', 'high', 'low', 'close', 'volume'
# Cũng có thể nhập dữ liệu từ CSV hoặc API tương ứng

# Các tham số đầu vào
ma_frama_len = 12
frama_FC = 1
frama_SC = 200
Factor = 3
Pd = 7
test_start_year = 2020
test_start_month = 1
test_start_day = 1
test_stop_year = 2020
test_stop_month = 12
test_stop_day = 31

# Tính toán MA Frama
def ma_frama(df:pd.DataFrame, ma_len, frama_FC = 1, frama_SC = 200):
    e = 2.718281828459045
    w = np.log(2 / (frama_SC + 1)) / np.log(e)  # Natural logarithm workaround
    len1 = ma_len // 2
    H1 = df['high'].rolling(window=len1).max()
    L1 = df['low'].rolling(window=len1).min()
    N1 = (H1 - L1) / len1
    H2_ = df['high'].rolling(window=len1).max()
    H2 = H2_.shift(len1)
    L2_ = df['low'].rolling(window=len1).min()
    L2 = L2_.shift(len1)
    N2 = (H2 - L2) / len1
    H3 = df['high'].rolling(window=ma_len).max()
    L3 = df['low'].rolling(window=ma_len).min()
    N3 = (H3 - L3) / ma_len
    dimen1 = (np.log(N1 + N2) - np.log(N3)) / np.log(2)
    dimen = np.where((N1 > 0) & (N2 > 0) & (N3 > 0), dimen1, np.nan)
    alpha1 = np.exp(w * (dimen - 1))
    oldalpha = np.clip(alpha1, 0.01, 1)
    oldN = (2 - oldalpha) / oldalpha
    N = ((frama_SC - frama_FC) * (oldN - 1)) / (frama_SC - 1) + frama_FC
    alpha_ = 2 / (N + 1)
    alpha = np.clip(alpha_, 2 / (frama_SC + 1), 1)
    
    frama = np.zeros(len(df))
    for i in range(1, len(df)):
        frama[i] = (1 - alpha[i]) * frama[i-1] + alpha[i] * df['close'][i]
    
    return frama

# Tính toán SuperTrend (để kiểm tra điều kiện vào và thoát giao dịch)
def supertrend(df, Factor, Pd):
    hl2 = (df['high'] + df['low']) / 2
    atr = ta.atr(df, length=Pd)
    Up = hl2 - Factor * atr
    Dn = hl2 + Factor * atr
    TrendUp = np.zeros(len(df))
    TrendDown = np.zeros(len(df))
    
    for i in range(1, len(df)):
        TrendUp[i] = max(Up[i], TrendUp[i-1]) if df['close'][i-1] > TrendUp[i-1] else Up[i]
        TrendDown[i] = min(Dn[i], TrendDown[i-1]) if df['close'][i-1] < TrendDown[i-1] else Dn[i]
    
    Trend = np.where(df['close'] > TrendDown, 1, np.where(df['close'] < TrendUp, -1, 0))
    return Trend, TrendUp, TrendDown

# Tạo các tín hiệu giao dịch từ Frama và Supertrend
def generate_signals(df):
    frama = ma_frama(df, ma_frama_len, frama_FC, frama_SC)
    signal = pd.Series(ma_frama(df, ma_frama_len, frama_FC, frama_SC), name="Signal")
    
    Trend, TrendUp, TrendDown = supertrend(df, Factor, Pd)
    
    long_condition = (frama > signal)  # Crossover condition
    short_condition = (frama < signal)  # Crossunder condition
    
    # Tạo tín hiệu vào và thoát giao dịch
    buy_signal = long_condition
    sell_signal = short_condition

    return buy_signal, sell_signal, Trend

# Áp dụng hàm generate_signals vào dữ liệu của bạn
df = pd.read_csv('your_data.csv', parse_dates=True, index_col="date")  # Giả sử bạn có DataFrame
buy_signal, sell_signal, Trend = generate_signals(df)

# Kiểm tra tín hiệu mua và bán
df['Buy_Signal'] = buy_signal
df['Sell_Signal'] = sell_signal
df['Trend'] = Trend

# Hiển thị kết quả
print(df[['Buy_Signal', 'Sell_Signal', 'Trend']].tail())