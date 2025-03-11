import asyncio
from ccxt.base.types import *
import ccxt.pro as Exchange_ws
import ccxt as Exchange
from PySide6.QtCore import QObject

# These exchanges will be used for testing the performance of the exchange connector.
class CryptoExchange(QObject):
    def __init__(self):
        super().__init__()
        self.exchange:str = None
        self.name:str = ""
    def setupEchange(self,apikey:str="", secretkey:str="",exchange_name:str="binanceusdm"):
        self.apikey = apikey
        self.secretkey = secretkey
        self.verbose = True
        self.exchange = None
        # Add your own exchanges here if needed
        self.name = exchange_name.lower()

        if self.name == "binance":
            self.exchange = Exchange.binance({
                'apiKey': self.apikey,
              'secret': self.secretkey,
            })
        elif self.name == "binancecoinm":
            self.exchange = Exchange.binancecoinm({
                'apiKey': self.apikey,
              'secret': self.secretkey,
            })
        elif self.name == "binanceusdm":
            self.exchange = Exchange.binanceusdm({
                'apiKey': self.apikey,
            'secret': self.secretkey,
            })
        elif self.name == "binanceus":
            self.exchange = Exchange.binanceus({
                'apiKey': self.apikey,
            'secret': self.secretkey,
            })  
        elif self.name == "bitmex":
            self.exchange = Exchange.bitmex({
                'apiKey': self.apikey,
             'secret': self.secretkey,
            })
        elif self.name == "bybit":
            self.exchange = Exchange.bybit({
                'apiKey': self.apikey,
           'secret': self.secretkey,
            })
        elif self.name == "huobi":
            self.exchange = Exchange.huobi({
                'apiKey': self.apikey,
               'secret': self.secretkey})
        elif self.name == "kraken":
            self.exchange = Exchange.kraken({
                'apiKey': self.apikey,
             'secret': self.secretkey})
        elif self.name == "krakenfutures":
            self.exchange = Exchange.krakenfutures({
                'apiKey': self.apikey,
            'secret': self.secretkey})
        elif self.name == "kucoin":
            self.exchange = Exchange.kucoin({
                'apiKey': self.apikey,
             'secret': self.secretkey})
        elif self.name == "kucoinfutures":
            self.exchange = Exchange.kucoinfutures({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "bingx":
            self.exchange = Exchange.bingx({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "bitfinex2":
            self.exchange = Exchange.bitfinex2({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "bitget":
            self.exchange = Exchange.bitget({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "bitmart":
            self.exchange = Exchange.bitmart({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "coinex":
            self.exchange = Exchange.coinex({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "deribit":
            self.exchange = Exchange.deribit({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "coinbaseexchange":
            self.exchange = Exchange.coinbaseexchange({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "coinbase":
            self.exchange = Exchange.coinbase({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "hitbtc":
            self.exchange = Exchange.hitbtc({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "mexc":
            self.exchange = Exchange.mexc({
                'apiKey': self.apikey,
                'secret': self.secretkey})
        elif self.name == "okx":
            self.exchange = Exchange.okx({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        else:
            self.exchange = None
        print(f"Change Ex----- {self.exchange}",self.apikey,self.secretkey)
        return self.exchange
    def load_markets(self, reload=False, params={}):
        return self.exchange.load_markets(reload=reload, params=params)

    def fetch_ohlcv(self, symbol: str, timeframe='1m', since: Int = None, limit: Int = None, params={}):
        return self.exchange.fetch_ohlcv(symbol, timeframe, since,limit,params)
    
class  CryptoExchange_WS():
    def __init__(self):
        self.exchange = None
        self.name = ""
    def setupEchange(self,apikey:str="", secretkey:str="",exchange_name:str="binanceusdm"):
        self.apikey = apikey
        self.secretkey = secretkey
        self.verbose = True
        self.exchange = None
        # Add your own exchanges here if needed
        self.name = exchange_name.lower()

        if self.name == "binance":
            self.exchange = Exchange_ws.binance({
                'apiKey': self.apikey,
              'secret': self.secretkey,
            })
        elif self.name == "binancecoinm":
            self.exchange = Exchange_ws.binancecoinm({
                'apiKey': self.apikey,
              'secret': self.secretkey,
            })
        elif self.name == "binanceusdm":
            self.exchange = Exchange_ws.binanceusdm({
                'apiKey': self.apikey,
            'secret': self.secretkey,
            })
        elif self.name == "bitmex":
            self.exchange = Exchange_ws.bitmex({
                'apiKey': self.apikey,
             'secret': self.secretkey,
            })
        elif self.name == "bybit":
            self.exchange = Exchange_ws.bybit({
                'apiKey': self.apikey,
           'secret': self.secretkey,
            })
        elif self.name == "huobi":
            self.exchange = Exchange_ws.huobi({
                'apiKey': self.apikey,
               'secret': self.secretkey})
        elif self.name == "kraken":
            self.exchange = Exchange_ws.kraken({
                'apiKey': self.apikey,
             'secret': self.secretkey})
        elif self.name == "krakenfutures":
            self.exchange = Exchange_ws.krakenfutures({
                'apiKey': self.apikey,
            'secret': self.secretkey})
        elif self.name == "kucoin":
            self.exchange = Exchange_ws.kucoin({
                'apiKey': self.apikey,
             'secret': self.secretkey})
        elif self.name == "kucoinfutures":
            self.exchange = Exchange_ws.kucoinfutures({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "bingx":
            self.exchange = Exchange_ws.bingx({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "bitfinex2":
            self.exchange = Exchange_ws.bitfinex2({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "bitget":
            self.exchange = Exchange_ws.bitget({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "bitmart":
            self.exchange = Exchange_ws.bitmart({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "coinex":
            self.exchange = Exchange_ws.coinex({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "deribit":
            self.exchange = Exchange_ws.deribit({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "coinbaseexchange":
            self.exchange = Exchange_ws.coinbaseexchange({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "coinbase":
            self.exchange = Exchange_ws.coinbase({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "hitbtc":
            self.exchange = Exchange_ws.hitbtc({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "mexc":
            self.exchange = Exchange_ws.mexc({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        elif self.name == "okx":
            self.exchange = Exchange_ws.okx({
                'apiKey': self.apikey,
           'secret': self.secretkey})
        else:
            print(f"_____________Exchange {self.name} not found___________")
            self.exchange = None
            return None
        return self.exchange
        
    async def load_markets_helper(self, reload=False, params={}):
        return await self.exchange.load_markets_helper(reload=False, params={})  # don't return cached markets if we can help it

    async def load_markets(self, reload=False, params={}):
        return await self.exchange.load_markets(reload=reload, params=params)

    def fetch_fees(self):
         return self.exchange.fetch_fees()

    async def load_fees(self, reload=False):
        return await self.exchange.load_fees(reload=False)

    async def fetch_markets(self, params={}):
        return await self.exchange.fetch_markets(params={})

    async def fetch_currencies(self, params={}):
        return await self.exchange.fetch_currencies(params={})

    async def fetchOHLCVC(self, symbol, timeframe='1m', since=None, limit=None, params={}):
        return await self.exchange.fetchOHLCVC(symbol, timeframe='1m', since=None, limit=None, params={})
        
    async def fetch_full_tickers(self, symbols=None, params={}):
        return await self.exchange.fetch_full_tickers(symbols=None, params={})

    async def sleep(self, milliseconds):
        return await asyncio.sleep(milliseconds / 1000)

    def order_book(self, snapshot={}, depth=None):
         return self.exchange.order_book(snapshot={}, depth=None)

    def indexed_order_book(self, snapshot={}, depth=None):
        return self.exchange.indexed_order_book(snapshot={}, depth=None)

    def counted_order_book(self, snapshot={}, depth=None):
        return self.exchange.counted_order_book(snapshot={}, depth=None)

    def delay(self, timeout, method, *args):
        return self.exchange.delay(timeout / 1000, self.spawn, method, *args)

    def format_scientific_notation_ftx(self, n):
        if n == 0:
            return '0e-00'
        return format(n, 'g')

    # METHODS BELOW THIS LINE ARE TRANSPILED FROM JAVASCRIPT TO PYTHON AND PHP

    async def fetch_accounts(self, params={}):
        return await self.exchange.fetch_accounts(params)

    async def fetch_trades(self, symbol: str, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_trades(symbol, since, limit, params)

    async def fetch_trades_ws(self, symbol: str, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_trades_ws(symbol, since, limit, params)

    async def watch_trades(self, symbol: str, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.watch_trades(symbol, since, limit, params)

    async def watch_trades_for_symbols(self, symbols: list[str], since: Int = None, limit: Int = None, params={}):
        return await self.exchange.watch_trades_for_symbols(symbols, since, limit, params)

    async def watch_my_trades_for_symbols(self, symbols: list[str], since: Int = None, limit: Int = None, params={}):
        return await self.exchange.watch_my_trades_for_symbols(symbols, since, limit, params)

    async def watch_orders_for_symbols(self, symbols: list[str], since: Int = None, limit: Int = None, params={}):
        return await self.exchange.watch_orders_for_symbols(symbols, since, limit, params)

    async def watch_ohlcv_for_symbols(self, symbolsAndTimeframes: list[list[str]], since: Int = None, limit: Int = None, params={}):
        return await self.exchange.watch_ohlcv_for_symbols(symbolsAndTimeframes, since, limit, params)

    async def watch_order_book_for_symbols(self, symbols: list[str], limit: Int = None, params={}):
        return await self.exchange.watch_order_book_for_symbols(symbols, limit, params)

    async def fetch_order_book(self, symbol: str, limit: Int = None, params={}):
        return await self.exchange.fetch_order_book(symbol, limit, params)

    async def fetch_margin_mode(self, symbol: str, params={}):
        return await self.exchange.fetch_margin_mode(symbol, params)

    async def fetch_margin_modes(self, symbols: list[str] = None, params={}):
        return await self.exchange.fetch_margin_modes(symbols, params)

    async def fetch_rest_order_book_safe(self, symbol, limit=None, params={}):
        return await self.exchange.fetch_rest_order_book_safe(symbol, limit, params)

    async def watch_order_book(self, symbol: str, limit: Int = None, params={}):
        return await self.exchange.watch_order_book(symbol, limit, params)

    async def fetch_time(self, params={}):
        return await self.exchange.fetch_time(params)

    async def fetch_trading_limits(self, symbols: list[str] = None, params={}):
        return await self.exchange.fetch_trading_limits(symbols, params)

    async def fetch_cross_borrow_rates(self, params={}):
        return await self.exchange.fetch_cross_borrow_rates(params)

    async def fetch_isolated_borrow_rates(self, params={}):
        return await self.exchange.fetch_isolated_borrow_rates(params)

    async def fetch_leverage_tiers(self, symbols: list[str] = None, params={}):
        return await self.exchange.fetch_leverage_tiers(symbols, params)

    async def fetch_funding_rates(self, symbols: list[str] = None, params={}):
        return await self.exchange.fetch_funding_rates(symbols, params)

    async def watch_funding_rate(self, symbol: str, params={}):
        return await self.exchange.watch_funding_rate(symbol, params)

    async def watch_funding_rates(self, symbols: list[str], params={}):
        return await self.exchange.watch_funding_rates(symbols, params)

    async def watch_funding_rates_for_symbols(self, symbols: list[str], params={}):
        return await self.exchange.watch_funding_rates_for_symbols(symbols, params)

    async def set_leverage(self, leverage: Int, symbol: Str = None, params={}):
        return await self.exchange.set_leverage(leverage, symbol, params)

    async def fetch_leverage(self, symbol: str, params={}):
        return await self.exchange.fetch_leverage(symbol, params)

    async def fetch_leverages(self, symbols: list[str] = None, params={}):
        return await self.exchange.fetch_leverages(symbols, params)

    async def set_position_mode(self, hedged: bool, symbol: Str = None, params={}):
        return await self.exchange.set_position_mode(hedged, symbol, params)

    async def add_margin(self, symbol: str, amount: float, params={}):
        return await self.exchange.add_margin(symbol, amount, params)

    async def reduce_margin(self, symbol: str, amount: float, params={}):
        return await self.exchange.reduce_margin(symbol, amount, params)

    async def set_margin(self, symbol: str, amount: float, params={}):
        return await self.exchange.set_margin(symbol,amount, params)

    async def set_margin_mode(self, marginMode: str, symbol: Str = None, params={}):
        return await self.exchange.set_margin_mode(marginMode, symbol, params)

    async def fetch_borrow_rate(self, code: str, amount, params={}):
        return await self.exchange.fetch_borrow_rate(code, amount, params)

    async def repay_cross_margin(self, code: str, amount, params={}):
        return await self.exchange.repay_cross_margin(code, amount, params)

    async def repay_isolated_margin(self, symbol: str, code: str, amount, params={}):
        return await self.exchange.repay_isolated_margin(symbol, code, amount, params)

    async def borrow_cross_margin(self, code: str, amount: float, params={}):
        return await self.exchange.borrow_cross_margin(code, amount, params)

    async def borrow_isolated_margin(self, symbol: str, code: str, amount: float, params={}):
        return await self.exchange.borrow_isolated_margin(symbol, code, amount, params)

    async def borrow_margin(self, code: str, amount, symbol: Str = None, params={}):
        return await self.exchange.borrow_margin(code, amount, symbol, params)
    async def repay_margin(self, code: str, amount, symbol: Str = None, params={}):
        return await self.exchange.repay_margin(code,amount,symbol,params)

    async def fetch_ohlcv(self, symbol: str, timeframe='1m', since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_ohlcv(symbol, timeframe, since,limit,params)

    async def fetch_ohlcv_ws(self, symbol: str, timeframe='1m', since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_ohlcv_ws(symbol, timeframe, since,limit,params)

    async def watch_ohlcv(self, symbol: str, timeframe='1m', since: Int = None, limit: Int = None, params={}):
        return await self.exchange.watch_ohlcv(symbol, timeframe, since,limit,params)

    async def load_trading_limits(self, symbols: list[str] = None, reload=False, params={}):
        return await self.exchange.load_trading_limits(symbols, reload, params)

    async def load_accounts(self, reload=False, params={}):
        return await self.exchange.load_accounts(reload, params)

    async def edit_limit_buy_order(self, id: str, symbol: str, amount: float, price: Num = None, params={}):
       return await self.exchange.edit_limit_buy_order(id, symbol, amount, price, params)

    async def edit_limit_sell_order(self, id: str, symbol: str, amount: float, price: Num = None, params={}):
        return await self.exchange.edit_limit_sell_order(id, symbol, amount, price, params)

    async def edit_limit_order(self, id: str, symbol: str, side: OrderSide, amount: float, price: Num = None, params={}):
        return await self.exchange.edit_limit_order(id, symbol, type, side, amount, price, params)

    async def edit_order(self, id: str, symbol: str, type: OrderType, side: OrderSide, amount: Num = None, price: Num = None, params={}):
        return await self.exchange.edit_order(id, symbol, type, side, amount, price, params)

    async def edit_order_ws(self, id: str, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, params={}):
        return await self.exchange.edit_order_ws(id, symbol, type, side, amount, price, params)

    async def fetch_permissions(self, params={}):
        return await self.exchange.fetch_permissions(params)

    async def fetch_position(self, symbol: str, params={}):
        return await self.exchange.fetch_position(symbol,params)

    async def watch_position(self, symbol: Str = None, params={}):
        return await self.exchange.watch_position(symbol,params)

    async def watch_positions(self, symbols: list[str] = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.watch_positions(symbols, since, limit, params)

    async def watch_position_for_symbols(self, symbols: list[str] = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.watch_position_for_symbols(symbols, since, limit, params)

    async def fetch_positions_for_symbol(self, symbol: str, params={}):
        return await self.exchange.fetch_positions_for_symbol(symbol,params)

    async def fetch_positions(self, symbols: list[str] = None, params={}):
        return await self.exchange.fetch_positions(symbols,params)

    async def fetch_positions_risk(self, symbols: list[str] = None, params={}):
        return await self.exchange.fetch_positions_risk(symbols,params)

    async def fetch_bids_asks(self, symbols: list[str] = None, params={}):
        return await self.exchange.fetch_bids_asks(symbols,params)

    async def fetch_borrow_interest(self, code: Str = None, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_borrow_interest(code,symbol,since,limit,params)

    async def fetch_ledger(self, code: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_ledger(code,since,limit,params)

    async def fetch_ledger_entry(self, id: str, code: Str = None, params={}):
        return await self.exchange.fetch_ledger_entry(id,code,params)

    async def fetch_balance(self, params={}):
        return await self.exchange.fetch_balance(params)

    async def fetch_balance_ws(self, params={}):
        return await self.exchange.fetch_balance_ws(params)

    async def watch_balance(self, params={}):
        return await self.exchange.watch_balance(params)

    async def fetch_partial_balance(self, part, params={}):
        return await self.exchange.fetch_partial_balance(part,params)

    async def fetch_free_balance(self, params={}):
        return await self.exchange.fetch_free_balance(params)

    async def fetch_used_balance(self, params={}):
        return await self.exchange.fetch_used_balance(params)

    async def fetch_total_balance(self, params={}):
        return await self.exchange.fetch_total_balance(params)

    async def fetch_status(self, params={}):
        return await self.exchange.fetch_status(params)

    async def fetch_funding_fee(self, code: str, params={}):
        return await self.exchange.fetch_funding_fee(code,params)

    async def fetch_funding_fees(self, codes: list[str] = None, params={}):
        return await self.exchange.fetch_funding_fees(codes,params)

    async def fetch_cross_borrow_rate(self, code: str, params={}):
        return await self.exchange.fetch_cross_borrow_rate(code,params)

    async def fetch_isolated_borrow_rate(self, symbol: str, params={}):
        return await self.exchange.fetch_isolated_borrow_rate(symbol,params)

    async def fetch_ticker(self, symbol: str, params={}):
        return await self.exchange.fetch_ticker(symbol,params)

    async def watch_ticker(self, symbol: str, params={}):
        return await self.exchange.watch_ticker(symbol,params)

    async def fetch_tickers(self, symbols: list[str] = None, params={}):
        return await self.exchange.fetch_tickers(symbols,params)

    async def fetch_order_books(self, symbols: list[str] = None, limit: Int = None, params={}):
        return await self.exchange.fetch_order_books(symbols, limit, params)

    async def watch_tickers(self, symbols: list[str] = None, params={}):
        return await self.exchange.watch_tickers(symbols, params)

    async def fetch_order(self, id: str, symbol: Str = None, params={}):
        return await self.exchange.fetch_order(id, symbol, params)

    async def fetch_order_ws(self, id: str, symbol: Str = None, params={}):
        return await self.exchange.fetch_order_ws(id, symbol, params)

    async def fetch_order_status(self, id: str, symbol: Str = None, params={}):
        return await self.exchange.fetch_order_status(id, symbol, params)

    async def fetch_unified_order(self, order, params={}):
        return await self.exchange.fetch_unified_order(order, params)

    async def create_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, params={}):
        return await self.exchange.create_order(symbol, type, side, amount, price, params)

    async def create_trailing_amount_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, trailingAmount=None, trailingTriggerPrice=None, params={}):
        return await self.exchange.create_trailing_amount_order(symbol, type, side, amount, price, trailingAmount, trailingTriggerPrice, params)

    async def create_trailing_percent_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, trailingPercent=None, trailingTriggerPrice=None, params={}):
        return await self.exchange.create_trailing_percent_order(symbol, type, side, amount, price, trailingPercent, trailingTriggerPrice, params)

    async def create_market_order_with_cost(self, symbol: str, side: OrderSide, cost: float, params={}):
        return await self.exchange.create_market_order_with_cost(symbol, side, cost, params)

    async def create_market_buy_order_with_cost(self, symbol: str, cost: float, params={}):
        return await self.exchange.create_market_buy_order_with_cost(symbol, cost, params)

    async def create_market_sell_order_with_cost(self, symbol: str, cost: float, params={}):
        return await self.exchange.create_market_sell_order_with_cost(symbol, cost, params)

    async def create_trigger_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, triggerPrice: Num = None, params={}):
        return await self.exchange.create_trigger_order(symbol, type, side, amount, price, triggerPrice, params)

    async def create_stop_loss_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, stopLossPrice: Num = None, params={}):
        return await self.exchange.create_stop_loss_order(symbol, type, side, amount, price, stopLossPrice, params)

    async def create_take_profit_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, takeProfitPrice: Num = None, params={}):
        return await self.exchange.create_take_profit_order(symbol, type, side, amount, price, takeProfitPrice, params)

    async def create_order_with_take_profit_and_stop_loss(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, takeProfit: Num = None, stopLoss: Num = None, params={}):
        return await self.exchange.create_order_with_take_profit_and_stop_loss(symbol, type, side, amount, price, takeProfit, stopLoss, params)

    async def create_orders(self, orders: list[OrderRequest], params={}):
        return await self.exchange.create_orders(orders, params)

    async def create_order_ws(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, params={}):
        return await self.exchange.create_order_ws(symbol, type, side, amount, price, params)

    async def cancel_order(self, id: str, symbol: Str = None, params={}):
        return await self.exchange.cancel_order(id, symbol, params)

    async def cancel_order_ws(self, id: str, symbol: Str = None, params={}):
        return await self.exchange.cancel_order_ws(id, symbol, params)

    async def cancel_orders_ws(self, ids: list[str], symbol: Str = None, params={}):
        return await self.exchange.cancel_orders_ws(ids, symbol, params)

    async def cancel_all_orders(self, symbol: Str = None, params={}):
        return await self.exchange.cancel_all_orders(symbol, params)

    async def cancel_all_orders_ws(self, symbol: Str = None, params={}):
        return await self.exchange.cancel_all_orders_ws(symbol, params)

    async def cancel_unified_order(self, order, params={}):
        return await self.exchange.cancel_unified_order(order, params)

    async def fetch_orders(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_orders(symbol, since, limit, params)

    async def fetch_orders_ws(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_orders_ws(symbol, since, limit, params)

    async def fetch_order_trades(self, id: str, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_order_trades(id, symbol, since, limit, params)

    async def watch_orders(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.watch_orders(symbol, since, limit, params)

    async def fetch_open_orders(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_open_orders(symbol, since, limit, params)

    async def fetch_open_orders_ws(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_open_orders_ws(symbol, since, limit, params)

    async def fetch_closed_orders(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_closed_orders(symbol, since, limit, params)

    async def fetch_canceled_and_closed_orders(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_canceled_and_closed_orders(symbol, since, limit, params)

    async def fetch_closed_orders_ws(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_closed_orders_ws(symbol, since, limit, params)

    async def fetch_my_trades(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_my_trades(symbol, since, limit, params)

    async def fetch_my_liquidations(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_my_liquidations(symbol, since, limit, params)

    async def fetch_liquidations(self, symbol: str, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_liquidations(symbol, since, limit, params)

    async def fetch_my_trades_ws(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_my_trades_ws(symbol, since, limit, params)

    async def watch_my_trades(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.watch_my_trades(symbol, since, limit, params)

    async def fetch_funding_rate_history(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_funding_rate_history(symbol, since, limit, params)

    async def fetch_funding_history(self, symbol: Str = None, since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_funding_history(symbol, since, limit, params)

    async def close_position(self, symbol: str, side: OrderSide = None, params={}):
        return await self.exchange.close_position(symbol, side, params)

    async def close_all_positions(self, params={}):
        return await self.exchange.close_all_positions(params)

    async def create_limit_order(self, symbol: str, side: OrderSide, amount: float, price: float, params={}):
        return await self.exchange.create_limit_order(symbol, side, amount, price, params)

    async def create_market_order(self, symbol: str, side: OrderSide, amount: float, price: Num = None, params={}):
        return await self.exchange.create_market_order(symbol, side, amount, price, params)

    async def create_limit_buy_order(self, symbol: str, amount: float, price: float, params={}):
        return await self.exchange.create_limit_buy_order(symbol, amount, price, params)

    async def create_limit_sell_order(self, symbol: str, amount: float, price: float, params={}):
        return await self.exchange.create_limit_sell_order(symbol, amount, price, params)

    async def create_market_buy_order(self, symbol: str, amount: float, params={}):
        return await self.exchange.create_market_buy_order(symbol, amount, params)

    async def create_market_sell_order(self, symbol: str, amount: float, params={}):
        return await self.exchange.create_market_sell_order(symbol, amount, params)

    async def load_time_difference(self, params={}):
        return await self.exchange.load_time_difference(params)

    async def fetch_market_leverage_tiers(self, symbol: str, params={}):
        return await self.exchange.fetch_market_leverage_tiers(symbol, params)

    async def create_post_only_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, params={}):
        return await self.exchange.create_post_only_order(symbol, type, side, amount, price, params)

    async def create_reduce_only_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, params={}):
        return await self.exchange.create_reduce_only_order(symbol, type, side, amount, price, params)

    async def create_stop_order(self, symbol: str, type: OrderType, side: OrderSide, amount: float, price: Num = None, stopPrice: Num = None, params={}):
        return await self.exchange.create_stop_order(symbol, type, side, amount, price, stopPrice, params)

    async def create_stop_limit_order(self, symbol: str, side: OrderSide, amount: float, price: float, stopPrice: float, params={}):
        return await self.exchange.create_stop_limit_order(symbol, side, amount, price, stopPrice, params)

    async def create_stop_market_order(self, symbol: str, side: OrderSide, amount: float, stopPrice: float, params={}):
        return await self.exchange.create_stop_market_order(symbol, side, amount, stopPrice, params)

    async def fetch_last_prices(self, symbols: list[str] = None, params={}):
        return await self.exchange.fetch_last_prices(symbols, params)

    async def fetch_trading_fees(self, params={}):
        return await self.exchange.fetch_trading_fees(params)

    async def fetch_trading_fees_ws(self, params={}):
        return await self.exchange.fetch_trading_fees_ws(params)

    async def fetch_trading_fee(self, symbol: str, params={}):
        return await self.exchange.fetch_trading_fee(symbol, params)

    async def fetch_funding_rate(self, symbol: str, params={}):
        return await self.exchange.fetch_funding_rate(symbol, params)

    async def fetch_mark_ohlcv(self, symbol, timeframe='1m', since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_mark_ohlcv(symbol, timeframe, since, limit, params)

    async def fetch_index_ohlcv(self, symbol: str, timeframe='1m', since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_index_ohlcv(symbol, timeframe, since, limit, params)

    async def fetch_premium_index_ohlcv(self, symbol: str, timeframe='1m', since: Int = None, limit: Int = None, params={}):
        return await self.exchange.fetch_premium_index_ohlcv(symbol=symbol, timeframe= timeframe, since= since, limit= limit, params=params)