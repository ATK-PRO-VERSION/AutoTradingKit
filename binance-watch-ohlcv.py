# -*- coding: utf-8 -*-

import os
import sys
# -----------------------------------------------------------------------------
import asyncio
import winloop
if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
    try:
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        winloop.install()
    except:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# -----------------------------------------------------------------------------

import ccxt  # noqa: E402
# -----------------------------------------------------------------------------
binance = ccxt.binanceusdm({
    'apiKey': '',
    'secret': '',
})
symbol = 'BTC/USDT'
timeframe = '1m'

# each ohlcv candle is a list of [ timestamp, open, high, low, close, volume ]
index = 4  # use close price from each ohlcv candle

height = 15
length = 80
import polars as pl
import pandas as pd
from atklip.controls.polars_ta.overlap.ema import ema as polars_ema
from atklip.controls.pandas_ta.overlap.ema import ema as pandas_ema


import time

# Bắt đầu đo thời gian


def print_chart(exchange, symbol, timeframe):

    # get a list of ohlcv candles
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe,limit=1500)

    polars_df = pl.DataFrame(ohlcv,schema=["datetime", "open", "high", "low", "close", "volume"]
        )
    
    df_pandas = pd.DataFrame(ohlcv,columns=["datetime", "open", "high", "low", "close", "volume"]
        )

    # Lấy cột close
    polars_close_column = polars_df["close"]
    pandas_close_column = df_pandas["close"]
            
    time_1 = time.time()
    pandas_ema_data = pandas_ema(pandas_close_column, 200,talib=True)
    
    time_2 = time.time()
    polars_ema_data = polars_ema(polars_close_column, 200)
    time_3 = time.time()
    
    print(f"Thời gian xử lý pandas_ema_data: {(time_2-time_1):10f} giây")
    print(f"Thời gian xử lý polars_ema_data: {(time_3-time_2):10f} giây")
    
    print(polars_ema_data)
    print(pandas_ema_data)
    
    
last = print_chart(binance, symbol, timeframe)
