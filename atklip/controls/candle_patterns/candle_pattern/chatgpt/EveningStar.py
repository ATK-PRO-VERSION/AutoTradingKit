import numpy as np

def recognize_evening_star(high, low, close, open):
    # Kiểm tra xem có đủ dữ liệu cho việc phân tích không
    if len(high) != 3 or len(low) != 3 or len(close) != 3 or len(open) != 3:
        print("Không đủ dữ liệu.")
        return
    
    # Tính các giá trị body của các nến
    body = np.abs(close - open)
    
    # Tính các giá trị shadow (có thể dùng high và low)
    shadow = np.minimum(close, open) - np.minimum(high, low)
    
    # Kiểm tra mẫu Evening Star (Sao Chỉ Về Đêm)
    if close[0] > open[0] and \
       close[1] > open[1] and \
       close[2] < open[2] and \
       close[2] < close[0] and \
       open[2] > close[0]:
        print("Evening Star pattern detected - bearish")

    elif close[0] < open[0] and \
         close[1] < open[1] and \
         close[2] > open[2] and \
         close[2] > close[0] and \
         open[2] < close[0]:
        print("Evening Star pattern detected - bullish")

    else:
        print("Không tìm thấy mẫu Evening Star trong dữ liệu.")

# Sử dụng hàm với dữ liệu mẫu
high = np.array([10, 11, 12])
low = np.array([9, 10, 11])
close = np.array([9.5, 10.5, 11.5])
open = np.array([9.8, 10.3, 11.2])

recognize_evening_star(high, low, close, open)
