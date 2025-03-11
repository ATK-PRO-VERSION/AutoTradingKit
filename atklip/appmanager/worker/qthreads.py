import asyncio
from threading import Thread
import traceback
from PySide6.QtCore import QObject, Signal, Slot, Slot, QThread,QCoreApplication

class QtheadAsyncWorker(QThread):
    update_signal = Signal(object)
    finished = Signal()
    error = Signal(str)
    def __init__(self,parent, fn, *args, **kwargs):
        super(QtheadAsyncWorker, self).__init__(parent)
        self.moveToThread(QCoreApplication.instance().thread())
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.kwargs['update_signal'] = self.update_signal
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.started.connect(self.run)
        self.finished.connect(self.stop_thread)
        self.parent().destroyed.connect(self.stop_thread)
    
    def start_thread(self):
        self.start()
    
    def stop_thread(self):
        self.loop.stop()
        self.loop.close()
        self.deleteLater()

    @Slot()
    def run(self):
        try:
            self.loop.create_task(self.fn(*self.args, **self.kwargs))
            self.loop.run_forever()
        except Exception as e:
            traceback.print_exception(e)
            self.error.emit(str(e))
        finally:
            self.finished.emit()
            self.loop.stop()
            self.loop.close()

class RequestAsyncWorker(QThread):
    setdata = Signal(tuple)  # setdata có graph object
    error = Signal(str)
    finished = Signal()
    update_signal = Signal(list)
    def __init__(self,parent, fn, *args, **kwargs):
        super(RequestAsyncWorker, self).__init__(parent)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.kwargs['update_signal'] = self.update_signal
        self.started.connect(self.run)
        self.finished.connect(self.stop_thread)
    
    def start_thread(self):
        self.start()
    
    def stop_thread(self):
        self.deleteLater()

    @Slot()
    def run(self):
        try:
            asyncio.run(self.fn(*self.args, **self.kwargs))
        except Exception as e:
            traceback.print_exception(e)
            self.error.emit(str(e))
        finally:
            try:
                self.finished.emit()
            except:
                pass


class WorkerSignals(QObject):
    setdata = Signal(tuple)  # setdata có graph object
    error = Signal()
    finished = Signal()
    update_signal = Signal(list)
    sig_object = Signal(object)
    sig_process_value = Signal(float)

class FastWorker(Thread):
    "Worker này dùng để emit candle data"
    def __init__(self,parent,fn, *args, **kwargs):
        super(FastWorker, self).__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals() 
        self.kwargs['setdata'] = self.signals.setdata
        self.started.connect(self.run)
        self.finished.connect(self.stop_thread)
        self.signals.error.connect(self.stop_thread)

    def start_thread(self):
        self.start()
    def stop_thread(self):
        self._stop()
        self.deleteLater()
    def run(self):
        try:
            self.fn(*self.args, **self.kwargs)
        except Exception as e:
            traceback.print_exception(e)
            self.signals.error.emit()
        finally:
            try:
                self.finished.emit()
            except:
                self.deleteLater()
