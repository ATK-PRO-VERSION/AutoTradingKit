import weakref
from time import perf_counter

from atklip.graphics.pyqtgraph.functions import SignalBlock

from atklip.graphics.pyqtgraph.ThreadsafeTimer import ThreadsafeTimer

from PySide6 import QtCore
from PySide6.QtCore import QObject, Signal, Qt,QTimer


class Signal_Proxy(QObject):
    sigDelayed = Signal(object)
    def __init__(self, signal, slot,connect_type:Qt.ConnectionType=Qt.ConnectionType.AutoConnection):
        QObject.__init__(self)
        self.connect_type = connect_type
        self.signal = signal
        self.slot = slot
        self.moveToThread(QtCore.QCoreApplication.instance().thread())
        self.signal.connect(self.slot,self.connect_type)
    
    def disconnect(self):
        try:
            self.signal.disconnect(self.slot)
        except:
            pass
        # self.deleteLater()
    def connectSlot(self, slot):
        self.signal.connect(slot,self.connect_type)

    def block(self):
        return SignalBlock(self.signal, self.slot)


class Safe_Proxy_Signal(QObject):
    sigDelayed = Signal(object)
    def __init__(self, signal, slot,connect_type:Qt.ConnectionType=Qt.ConnectionType.AutoConnection):
        QObject.__init__(self)
        self.connect_type = connect_type
        self.signal = signal
        self.slot = slot
        self.moveToThread(QtCore.QCoreApplication.instance().thread())
        self.signal.connect(self.signalReceived,self.connect_type)
        self.sigDelayed.connect(self.slot,self.connect_type)
    
    def signalReceived(self, _object:QObject|object=None):
        """Received signal. Cancel previous timer and store args to be
        forwarded later."""
        if _object is not None:
            _object.moveToThread(QtCore.QCoreApplication.instance().thread())
        self.sigDelayed.emit(_object)

    def disconnect(self):
        try:
            self.signal.disconnect(self.slot)
        except:
            pass
        # self.deleteLater()
    def connectSlot(self, slot):
        self.signal.connect(slot,self.connect_type)

    def block(self):
        return SignalBlock(self.signal, self.slot)




class SafeSignalUpdateGraph(QObject):
    """Object which collects rapid-fire signals and condenses them
    into a single signal or a rate-limited stream of signals.
    Used, for example, to prevent a SpinBox from generating multiple
    signals when the mouse wheel is rolled over it.

    Emits sigDelayed after input signals have stopped for a certain period of
    time.
    """

    sigDelayed = Signal(object)

    def __init__(self, signal, delay=0, rateLimit=100, slot=None, *, threadSafe=True):
        """Initialization arguments:
        signal - a bound Signal or pyqtSignal instance
        delay - Time (in seconds) to wait for signals to stop before emitting (default 0.3s)
        slot - Optional function to connect sigDelayed to.
        rateLimit - (signals/sec) if greater than 0, this allows signals to stream out at a
                    steady rate while they are being received.
        threadSafe - Specify if thread-safety is required. For backwards compatibility, it
                     defaults to True.
        """

        QObject.__init__(self)
        self.delay = delay
        self.rateLimit = rateLimit
        self.args = None
        Timer = ThreadsafeTimer if threadSafe else QTimer
        self.timer = Timer()
        self.timer.timeout.connect(self.flush)
        self.lastFlushTime = None
        self.signal = signal
        self.signal.connect(self.signalReceived)
        if slot is not None:
            self.blockSignal = False
            self.sigDelayed.connect(slot)
            self.slot = weakref.ref(slot)
        else:
            self.blockSignal = True
            self.slot = None

    def setDelay(self, delay):
        self.delay = delay

    def signalReceived(self, *args):
        """Received signal. Cancel previous timer and store args to be
        forwarded later."""
        if self.blockSignal:
            return
        self.args = args
        if self.rateLimit == 0:
            self.timer.stop()
            self.timer.start(int(self.delay * 1000) + 1)
        else:
            now = perf_counter()
            if self.lastFlushTime is None:
                leakTime = 0
            else:
                lastFlush = self.lastFlushTime
                leakTime = max(0, (lastFlush + (1.0 / self.rateLimit)) - now)

            self.timer.stop()
            self.timer.start(int(min(leakTime, self.delay) * 1000) + 1)

    def flush(self):
        """If there is a signal queued up, send it now."""
        if self.args is None or self.blockSignal:
            return False
        args, self.args = self.args, None
        self.timer.stop()
        self.lastFlushTime = perf_counter()
        self.sigDelayed.emit(args)
        return True

    def disconnect(self):
        self.blockSignal = True
        try:
            self.signal.disconnect(self.signalReceived)
        except:
            pass
        try:
            slot = self.slot()
            if slot is not None:
                self.sigDelayed.disconnect(slot)
        except:
            pass
        finally:
            self.slot = None

    def connectSlot(self, slot):
        """Connect the `SignalProxy` to an external slot"""
        assert self.slot is None, "Slot was already connected!"
        self.slot = weakref.ref(slot)
        self.sigDelayed.connect(slot)
        self.blockSignal = False

    def block(self):
        """Return a SignalBlocker that temporarily blocks input signals to
        this proxy.
        """
        return SignalBlock(self.signal, self.signalReceived)
