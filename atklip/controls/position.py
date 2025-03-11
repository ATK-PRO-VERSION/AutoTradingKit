from functools import lru_cache
from typing import Union
from psygnal import Signal
import numpy as np
from atklip.app_utils.calculate import cal_pnl_with_fee, calculate_recommended_capital_base_on_loss_capital,calculate_stoploss


class Position:
    sig_change_data = Signal(tuple)
    def __init__(self,_type:str="long") -> None:
        self.entry_price = None
        self.exit_price = None
        self.current_price = None
        self.qty = 0
        self.opened_at = None
        self.closed_at = None
        self._mark_price = None
        self._liquidation_price = None
        self.side = "market"
        self._type = _type

    @property
    def data(self):
        return {
            'entry_price': self.entry_price,
            'qty': self.qty,
            'current_price': self.current_price,
            'cost': self.cost,
            'type': self.type,
            'pnl': self.pnl,
            'pnl_percentage': self.pnl_percentage,
            'leverage': self.leverage,
            'liquidation_price': self.liquidation_price,
        }
    
    @property
    def fee(self):
        if self.side == "limit":
            return 0.002
        else:
            return 0.005
    @property
    def mark_price(self) -> float:
        if self.exchange_type == 'spot':
            return self.current_price

        return self._mark_price

    @property
    def cost(self) -> float:
        """
        The cost of open position in the quote currency

        :return: float
        """
        if self.is_close:
            return 0

        if self.current_price is None:
            return None

        return abs(self.current_price * self.qty)

    @property
    def type(self) -> str:
        """
        The type of open position - long, short, or close

        :return: str
        """
        return self._type

    @property
    def pnl_percentage(self) -> float:
        """
        Alias for self.roi

        :return: float
        """
        return self.roi

    @property
    def roi(self) -> float:
        """
        Return on Investment in percentage
        More at: https://www.binance.com/en/support/faq/5b9ad93cb4854f5990b9fb97c03cfbeb
        """
        if self.pnl == 0:
            return 0

        return self.pnl / self.total_cost * 100

    @property
    def total_cost(self) -> float:
        """
        How much we paid to open this position (currently does not include fees, should we?!)
        """
        if self.is_close:
            return np.nan
        base_cost = self.entry_price * abs(self.qty)
        return base_cost / self.leverage

    @property
    def leverage(self) -> Union[int, np.float64]:
        if self.exchange_type == 'spot':
            return 1
        return self.leverage

    @property
    def exchange_type(self) -> str:
        return self.exchange.type

    @property
    def entry_margin(self) -> float:
        """
        Alias for self.total_cost
        """
        return self.total_cost

    @property
    def pnl(self) -> float:
        """
        The PNL of the position

        :return: float
        """
        if abs(self.qty) < self._min_qty:
            return 0

        if self.entry_price is None:
            return 0

        if self.cost is None:
            return 0
        pnl = cal_pnl_with_fee(self.entry_price,self.current_price,self.cost,1,self.leverage,0.005,0.002,"market",self.side,False)
        return pnl
    
        diff = self.cost - abs(self.entry_price * self.qty)
        return -diff if self.type == 'short' else diff

    @property
    def is_open(self) -> bool:
        """
        Is the current position open?

        :return: bool
        """
        return self.type in ['long', 'short']

    @property
    def is_close(self) -> bool:
        """
        Is the current position close?
        :return: bool
        """
        return self.type == 'close'


    @property
    def mode(self) -> str:
        "spot/future"
        return self.exchange_type

    @property
    def liquidation_price(self) -> Union[float, np.float64]:
        """
        The price at which the position gets liquidated. formulas are taken from:
        https://help.bybit.com/hc/en-us/articles/900000181046-Liquidation-Price-USDT-Contract-
        """
        if self.is_close:
            return np.nan

        if self.mode in ['cross', 'spot']:
            return np.nan

        elif self.mode == 'isolated':
            if self.type == 'long':
                return self.entry_price * (1 - self._initial_margin_rate +self.fee)
            elif self.type == 'short':
                return self.entry_price * (1 + self._initial_margin_rate - self.fee)
            else:
                return np.nan

        else:
            raise ValueError

    @property
    def _initial_margin_rate(self) -> float:
        return 1 / self.leverage

    @property
    def bankruptcy_price(self) -> Union[float, np.float64]:
        if self.type == 'long':
            return self.entry_price * (1 - self._initial_margin_rate)
        elif self.type == 'short':
            return self.entry_price * (1 + self._initial_margin_rate)
        else:
            return np.nan

    def _close(self):
        pass

    def _update_qty(self, qty: float, operation='set'):
        pass

    def _open(self):
        pass

    @property
    def _min_notional_size(self) -> float:
        pass

    @property
    @lru_cache
    def _min_qty(self) -> float:
        pass

    @property
    def _can_mutate_qty(self):
        pass