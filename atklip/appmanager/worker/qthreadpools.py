from concurrent.futures import Future
from multiprocessing import Process, Queue
import asyncio,os
from asyncio import run
import sys
from threading import Thread
import traceback
from typing import Callable
from PySide6.QtCore import QObject, Signal, QRunnable, Slot, QThreadPool

from .threadpool import QThreadPool_global,ThreadPoolExecutor_global,ProcessPoolExecutor_global


class WorkerSignals(QObject):
    setdata = Signal(tuple)  # setdata có graph object
    error = Signal()
    finished = Signal()
    update_signal = Signal(list)
    sig_object = Signal(object)
    sig_process_value = Signal(float)


class QProcessWorker(QObject):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    finished = Signal()
    def __init__(self,fn:Callable=None, *args, **kwargs):
        super(QProcessWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.threadpool = ProcessPoolExecutor_global
        
    def start_thread(self):
        try:
            funture = self.threadpool.submit(self.run)
        except RuntimeError:
            pass
    
    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
        finally:
            self.finished.emit()
            self.deleteLater()


class ProcessWorker(QRunnable):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self, fn, *args, **kwargs):
        super(ProcessWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals() 
        self.kwargs['sig_process_value'] = self.signals.sig_process_value
        self.kwargs['finished'] = self.signals.finished
        self.threadpool = QThreadPool_global
        self.is_interrupted = False
        self.setAutoDelete(True)
    
    def start(self):
        self.threadpool.start(self)
    
    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
            self.signals.error.emit()
        finally:
            self.signals.finished.emit()  # Done

class FastWorker(QObject):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,fn:Callable=None, *args, **kwargs):
        super(FastWorker, self).__init__()
        # self.setAutoDelete(True)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals() 
        self.kwargs['setdata'] = self.signals.setdata
        self.threadpool = ThreadPoolExecutor_global
        # self.threadpool = QThreadPool_global
        
    def start(self):
        try:
            funture = self.threadpool.submit(self.run)
        except RuntimeError:
            pass
        # self.threadpool.start(self)
    
    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
        finally:
            self.signals.finished.emit()
            self.signals.deleteLater()
            self.deleteLater()



class SimpleWorker(QObject):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    finished = Signal()
    def __init__(self,fn:Callable=None, *args, **kwargs):
        super(SimpleWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.threadpool = ThreadPoolExecutor_global
        
    def start_thread(self):
        try:
            funture = self.threadpool.submit(self.run)
        except RuntimeError:
            pass
    

    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
        finally:
            self.finished.emit()
            self.deleteLater()


class CandleWorker(QObject):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    finished = Signal()
    def __init__(self,fn:Callable=None, *args, **kwargs):
        super(CandleWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.threadpool = ThreadPoolExecutor_global
        
    def start(self):
        try:
            funture = self.threadpool.submit(self.run)
        except RuntimeError:
            pass

    @Slot()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
        finally:
            self.finished.emit()
            self.deleteLater()

class FastStartSignal(QObject):
    error = Signal()
    finished = Signal()

class ThreadingAsyncWorker(QObject):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,fn, *args, **kwargs):
        super(ThreadingAsyncWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = FastStartSignal(self) 
        self.qtheadpool = ThreadPoolExecutor_global
        
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        self.signals.finished.connect(self.stop_thread)
        self.signals.error.connect(self.stop_thread)

    def start_thread(self):
        self.qtheadpool.submit(self.run)
    
    def stop_thread(self):
        try:
            self.signals.deleteLater()
        except Exception as e:
            pass
        asyncio.set_event_loop(None)
        self.loop.call_soon_threadsafe(self.loop.stop)
        try:
            self.deleteLater()
        except Exception as e:
            pass
        
    @Slot()
    def run(self):
        try:
            self.loop.run_until_complete(self.fn(*self.args, **self.kwargs))
            # asyncio.run(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            self.signals.error.emit()
        finally:
            try:
                self.signals.finished.emit()
            except:
                pass


class RequestAsyncWorker(QObject):
    "Worker này dùng để update  data trong một cho graph object khi có data mới"
    def __init__(self,fn, *args, **kwargs):
        super(RequestAsyncWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.qtheadpool = ThreadPoolExecutor_global
        self.signals = WorkerSignals() 
        self.kwargs['update_signal'] = self.signals.update_signal
        self.signals.finished.connect(self.stop_thread)
        self.signals.error.connect(self.stop_thread)

    def start_thread(self):
        self.qtheadpool.submit(self.run)
    
    def stop_thread(self):
        self.signals.deleteLater()
        self.deleteLater()
    @Slot()
    def run(self):
        try:
            asyncio.run(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            self.signals.error.emit()
        finally:
            try:
                self.signals.finished.emit()
            except:
                pass
