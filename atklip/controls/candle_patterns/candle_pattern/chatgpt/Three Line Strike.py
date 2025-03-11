import numpy as np

def recognize_three_line_strike(high, low, close, open):
    # Kiểm tra xem có đủ dữ liệu cho việc phân tích không
    if len(high) != 4 or len(low) != 4 or len(close) != 4 or len(open) != 4:
        print("Không đủ dữ liệu.")
        return
    
    # Tính các giá trị body của các nến
    body = np.abs(close - open)
    
    # Tính các giá trị shadow (có thể dùng high và low)
    shadow = np.minimum(close, open) - np.minimum(high, low)
    
    # Kiểm tra mẫu Three Line Strike (Ba Đường Gạch)
    if close[0] < open[0] and \
       close[1] < open[1] and \
       close[2] < open[2] and \
       close[3] > open[3] and \
       close[3] > close[0] and \
       open[3] < open[0]:
        print("Three Line Strike pattern detected - bearish")

    elif close[0] > open[0] and \
         close[1] > open[1] and \
         close[2] > open[2] and \
         close[3] < open[3] and \
         close[3] < close[0] and \
         open[3] > open[0]:
        print("Three Line Strike pattern detected - bullish")

    else:
        print("Không tìm thấy mẫu Three Line Strike trong dữ liệu.")

# Sử dụng hàm với dữ liệu mẫu
high = np.array([10, 11, 12, 13])
low = np.array([9, 10, 11, 12])
close = np.array([9.5, 10.5, 11.5, 13.5])
open = np.array([9.8, 10.3, 11.2, 13])

recognize_three_line_strike(high, low, close, open)
