from __future__ import annotations
import threading
from typing import Coroutine
from threading import Thread
import traceback
import asyncio
from PySide6.QtCore import Signal, QObject, QCoreApplication, Slot,QThread,Qt
from .threadpool import ThreadPoolExecutor_global


class FastStartThread(QObject):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,fn=None, *args, **kwargs):
        super(FastStartThread, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs.copy()
        self.threadpool = ThreadPoolExecutor_global
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
                        
    def start_thread(self):
        try:
            funture = self.threadpool.submit(self.run)
        except RuntimeError:
            pass
        
    def stop_thread(self):
        try:
            self.deleteLater()
        except:
            pass
    def run(self):
        try:
            self.loop.run_until_complete(self.fn(*self.args, **self.kwargs))
            # asyncio.run(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            self.loop.close()
        finally:
            self.deleteLater()

class ThreadingAsyncWorker(QObject):
    finished = Signal()
    error = Signal(str)
    update_signal = Signal() # dùng để emit toàn bộ candle data khi có nến mới
    lastcandle = Signal(list) # dùng để emit 2 nến cuối cùng
    def __init__(self,parent:None, fn, *args, **kwargs):
        super(ThreadingAsyncWorker, self).__init__(None)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self._thread = ThreadPoolExecutor_global
        self.finished.connect(self.stop_thread)
    
    def start_thread(self):
        self._thread.submit(self.run)
    
    def stop_thread(self):
        self.deleteLater()
    def run(self):
        try:
            asyncio.run(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            traceback.print_exception(e)
            self.error.emit(str(e))
        finally:
            self.finished.emit()

class RequestAsyncWorker(QObject):
    setdata = Signal(tuple)  # setdata có graph object
    error = Signal(str)
    finished = Signal(bool)
    update_signal = Signal(list)
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,parent, fn, *args, **kwargs):
        super(RequestAsyncWorker, self).__init__(parent)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.kwargs['update_signal'] = self.update_signal
        self._thread = ThreadPoolExecutor_global
        self.finished.connect(self.stop_thread)
    
    def start_thread(self):
        self._thread.submit(self.run)
    
    def stop_thread(self):

        self.deleteLater()
    def run(self):
        try:
            asyncio.run(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            traceback.print_exception(e)
            self.error.emit(str(e))
        finally:
            self.finished.emit(True)

class WorkerSignals(QObject):
    new_candles = Signal(list)
    setdata = Signal(tuple)  # setdata có graph object
    error = Signal()
    finished = Signal()
    update_signal = Signal(list)
    sig_object = Signal(object)
    sig_process_value = Signal(float)

class FastWorker(QObject):
    "Worker này dùng để emit candle data"
    finished = Signal()
    error = Signal(str)
    def __init__(self,parent, fn, *args, **kwargs):
        super(FastWorker, self).__init__(parent)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals(self) 
        self.kwargs['setdata'] = self.signals.setdata
        self._thread = ThreadPoolExecutor_global
        self.finished.connect(self.stop_thread)

    def start(self):
        self._thread.submit(self.run)
    def stop_thread(self):
        self.signals.deleteLater()
        self.deleteLater()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
            self.error.emit(str(e))
        finally:
            self.finished.emit()
