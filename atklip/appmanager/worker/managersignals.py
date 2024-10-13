from psygnal import evented,Signal,throttled
from dataclasses import dataclass


class SignalObject:
    sig_update_candle = Signal(list)
    sig_add_candle = Signal(list)
    sig_add_historic = Signal(int)
    sig_reset_all = Signal()
    signal_delete = Signal()
    sig_update_source = Signal()
    sig_reset_source = Signal(str)