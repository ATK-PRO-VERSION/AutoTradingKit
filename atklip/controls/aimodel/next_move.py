import pandas as pd
import numpy as np
import pandas_ta as ta
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

# Hàm tính toán các chỉ báo kỹ thuật
def calculate_technical_indicators(df):
    # Chỉ báo xu hướng
    df.ta.sma(length=20, append=True)  # SMA 20
    df.ta.ema(length=20, append=True)  # EMA 20
    df.ta.macd(append=True)            # MACD
    df.ta.psar(append=True)            # Parabolic SAR

    # Chỉ báo động lượng
    df.ta.rsi(length=14, append=True)  # RSI
    df.ta.stoch(append=True)           # Stochastic Oscillator
    df.ta.cci(length=20, append=True)  # CCI

    # Chỉ báo biến động
    df.ta.bbands(length=20, append=True)  # Bollinger Bands
    df.ta.atr(length=14, append=True)     # ATR

    # Chỉ báo khối lượng
    df.ta.obv(append=True)  # On-Balance Volume

    return df

# Hàm tạo target
def create_target(df, lookahead=15, threshold=0.02):
    # Tính giá cao nhất và thấp nhất trong 15 cây nến tiếp theo
    df['future_high'] = df['high'].shift(-lookahead).rolling(window=lookahead).max()
    df['future_low'] = df['low'].shift(-lookahead).rolling(window=lookahead).min()

    # Tính phần trăm thay đổi
    df['pct_change_high'] = (df['future_high'] - df['close']) / df['close']
    df['pct_change_low'] = (df['future_low'] - df['close']) / df['close']

    # Tạo target
    conditions = [
        (df['pct_change_low'] >= threshold) & (df['pct_change_high'] < threshold),
        (df['pct_change_high'] >= threshold) & (df['pct_change_low'] < threshold),
        (df['pct_change_high'] < threshold) & (df['pct_change_low'] < threshold)
    ]
    choices = [-1, 1, 0]
    df['target'] = np.select(conditions, choices, default=np.nan)

    # Loại bỏ các dòng không có target
    df.dropna(subset=['target'], inplace=True)

    return df

# Hàm chuẩn hóa dữ liệu
def normalize_data(df):
    scaler = StandardScaler()
    df_scaled = scaler.fit_transform(df)
    return df_scaled, scaler

# Hàm tạo dữ liệu cho LSTM
def create_sequences(data, target, sequence_length=50):
    X, y = [], []
    for i in range(len(data) - sequence_length):
        X.append(data[i:i+sequence_length])
        y.append(target[i+sequence_length])
    return np.array(X), np.array(y)

# Hàm xây dựng mô hình LSTM
def build_lstm_model(input_shape):
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=input_shape))
    model.add(Dropout(0.2))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(25, activation='relu'))
    model.add(Dense(1, activation='tanh'))  # Dùng tanh để đầu ra trong khoảng [-1, 1]
    model.compile(optimizer=Adam(learning_rate=0.001), loss='mse', metrics=['mae'])
    return model

# Hàm chính
def main():
    # Đọc dữ liệu (ví dụ: từ file CSV)
    df = pd.read_csv('btc_data.csv')  # Thay 'btc_data.csv' bằng đường dẫn đến file dữ liệu của bạn

    # Tính toán các chỉ báo kỹ thuật
    df = calculate_technical_indicators(df)

    # Tạo target
    df = create_target(df)

    # Chọn các cột làm đầu vào
    features = ['close', 'open', 'high', 'low', 'volume', 'SMA_20', 'EMA_20', 'MACD_12_26_9', 'MACDh_12_26_9', 'MACDs_12_26_9',
                'PSARl_0.02_0.2', 'PSARs_0.02_0.2', 'RSI_14', 'STOCHk_14_3_3', 'STOCHd_14_3_3', 'CCI_20_0.015',
                'BBL_20_2.0', 'BBM_20_2.0', 'BBU_20_2.0', 'BBB_20_2.0', 'ATRr_14', 'OBV']
    X = df[features]
    y = df['target']

    # Chuẩn hóa dữ liệu
    X_scaled, scaler = normalize_data(X)

    # Tạo dữ liệu cho LSTM
    sequence_length = 50
    X_sequences, y_sequences = create_sequences(X_scaled, y, sequence_length)

    # Chia dữ liệu thành tập huấn luyện và tập kiểm tra
    X_train, X_test, y_train, y_test = train_test_split(X_sequences, y_sequences, test_size=0.2, random_state=42)

    # Xây dựng mô hình LSTM
    model = build_lstm_model((X_train.shape[1], X_train.shape[2]))

    # Huấn luyện mô hình
    model.fit(X_train, y_train, epochs=20, batch_size=32, validation_data=(X_test, y_test))

    # Đánh giá mô hình
    loss, mae = model.evaluate(X_test, y_test)
    print(f"Test Loss: {loss}, Test MAE: {mae}")

if __name__ == "__main__":
    main()