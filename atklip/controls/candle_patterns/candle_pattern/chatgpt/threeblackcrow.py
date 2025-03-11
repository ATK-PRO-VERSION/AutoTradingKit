import numpy as np

def recognize_candle_patterns(high, low, close, open):
    # Kiểm tra xem có đủ dữ liệu cho việc phân tích không
    if len(high) < 3 or len(low) < 3 or len(close) < 3 or len(open) < 3:
        print("Không đủ dữ liệu.")
        return
    # Tính các giá trị body của các nến
    body = np.abs(close - open)
    # Tính các giá trị shadow (có thể dùng high và low)
    shadow = np.minimum(close, open) - np.minimum(high, low)
    # Tìm các nến bearish và bullish
    bearish_candles = (close < open) & (close - low > open - high)
    bullish_candles = (close > open) & (high - close < open - low)
    
    # Kiểm tra xem ba nến liên tiếp có đúng là Three Black Crows hay Three White Soldiers không
    for i in range(2, len(bearish_candles)):
        if bearish_candles[i-2] and bearish_candles[i-1] and bearish_candles[i]:
            print(f"Mẫu Three Black Crows được tìm thấy tại vị trí {i-2}, {i-1}, {i}")
        elif bullish_candles[i-2] and bullish_candles[i-1] and bullish_candles[i]:
            print(f"Mẫu Three White Soldiers được tìm thấy tại vị trí {i-2}, {i-1}, {i}")
    
    # Nếu không có mẫu nào được tìm thấy
    print("Không tìm thấy mẫu nến cảnh báo trong dữ liệu.")

# Sử dụng hàm với dữ liệu mẫu
high = np.array([10, 11, 12, 13, 14, 15, 16])
low = np.array([9, 10, 11, 12, 13, 14, 15])
close = np.array([9.5, 10.5, 11.5, 12.5, 13.5, 14.5, 15.5])
open = np.array([9.8, 10.3, 11.2, 12.3, 13.3, 14.3, 15.3])

recognize_candle_patterns(high, low, close, open)
