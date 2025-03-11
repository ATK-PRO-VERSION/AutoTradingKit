class sides:
    BUY = 'buy'
    SELL = 'sell'


class trade_types:
    LONG = 'long'
    SHORT = 'short'


class order_statuses:
    ACTIVE = 'ACTIVE'
    CANCELED = 'CANCELED'
    EXECUTED = 'EXECUTED'
    PARTIALLY_FILLED = 'PARTIALLY FILLED'
    QUEUED = 'QUEUED'
    LIQUIDATED = 'LIQUIDATED'
    REJECTED = 'REJECTED'


class timeframes:
    MINUTE_1 = '1m'
    MINUTE_3 = '3m'
    MINUTE_5 = '5m'
    MINUTE_15 = '15m'
    MINUTE_30 = '30m'
    MINUTE_45 = '45m'
    HOUR_1 = '1h'
    HOUR_2 = '2h'
    HOUR_3 = '3h'
    HOUR_4 = '4h'
    HOUR_6 = '6h'
    HOUR_8 = '8h'
    HOUR_12 = '12h'
    DAY_1 = '1D'
    DAY_3 = '3D'
    WEEK_1 = '1W'
    MONTH_1 = '1M'


class colors:
    GREEN = 'green'
    YELLOW = 'yellow'
    RED = 'red'
    MAGENTA = 'magenta'
    BLACK = 'black'


class order_types:
    MARKET = 'MARKET'
    LIMIT = 'LIMIT'
    STOP = 'STOP'
    FOK = 'FOK'
    STOP_LIMIT = 'STOP LIMIT'
    STOP_LOSS = 'stop-loss'
    TAKE_PROFIT = 'take-profit'


class exchanges:
    FAVORITE = "favorite"
    
    COINBASE_EXCHANGE = "coinbaseexchange"
    COINBASE = "coinbase"

    OKEX = "okx" 

    HUOBI = "huobi"

    # HITBTC = "hitbtc"

    # DERIBIT = "deribit"

    # COINEX = "coinex"   

    KRAKEN_SPOT = "kraken"  
    # KRAKEN_FUTURES = "krakenfutures"  

    KUCOIN_SPOT = 'kucoin'
    KUCOIN_FUTURES = 'kucoinfutures'   

    MEXC = "mexc"

    BINANCE_SPOT = 'binance'
    # BINANCE_US_SPOT = 'binanceus'
    BINANCE_PERPETUAL_FUTURES = 'binanceusdm' 
    # BINANCE_COIN_FUTURES = 'binancecoinm'

    BYBIT = 'bybit'  

    # BITVAVO = "bitvavo"

    #BITTREX = "bittrex"

    BITMEX = 'bitmex'

    BITMART = "bitmart"

    BITGET = "bitget"  

    # BITFINEX2 = "bitfinex2"

    # BINGX = "bingx"


_exchanges = {'COINBASE_EXCHANGE': 'coinbaseexchange', 
              'FAVORITE': 'favorite', 
                'COINBASE': 'coinbase', 
                'OKEX': 'okx', 
                'HUOBI': 'huobi', 
                # 'COINEX': 'coinex', 
                'KRAKEN_SPOT': 'kraken', 
                # 'KRAKEN_FUTURES': 'krakenfutures', 
                'KUCOIN_SPOT': 'kucoin', 
                'KUCOIN_FUTURES': 'kucoinfutures', 
                'MEXC': 'mexc', 
                'BINANCE_SPOT': 'binance', 
                # 'BINANCE_US_SPOT': 'binanceus', 
                'BINANCE_PERPETUAL_FUTURES': 'binanceusdm', 
                # 'BINANCE_COIN_FUTURES': 'binancecoinm', 
                'BYBIT': 'bybit', 
                # 'BITVAVO': 'bitvavo', 
                'BITMEX': 'bitmex', 
                'BITMART': 'bitmart', 
                'BITGET': 'bitget', 
                # 'BINGX': 'bingx'
                }
