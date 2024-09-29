# PyQt with server code
from multiprocessing import Process
import multiprocessing
from fastapi import FastAPI
import threading
import uvicorn
from PySide6.QtWidgets import (QMainWindow, QApplication, QTextEdit)
import sys
from PySide6.QtCore import (QRect, Signal, QObject)


import asyncio
import concurrent.futures

from atklip.app_api import app as api_app


app = api_app


class Signals(QObject):
    text_signal = Signal(str)

signals = Signals()


# main window app in main thread
class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setGeometry(QRect(0, 0, 400, 400))
        self._initial_widgets()
        self._create_server()
        
        # future = concurrent.futures.ThreadPoolExecutor().submit(self._create_server)
        
        signals.text_signal.connect(self.set_textEdit)

    def _initial_widgets(self):
        self.textedit = QTextEdit(self)
        self.textedit.setGeometry(QRect(100, 0, 100, 100))
        self.textedit.setReadOnly(True)
        self.setCentralWidget(self.textedit)

    def _create_server(self):
        thread = multiprocessing.Process(target=uvicorn.run, kwargs={
                                                    "app": "test_qconcurent:app", 
                                                    "host": "localhost",
                                                    "port": 81,
                                                    "ws_max_queue":1000,
                                                    "limit_max_requests":100000,
                                                    "workers": 2 
                                                },daemon=False)
        thread.start()
        # thread.terminate()
        print(thread.pid)

    def set_textEdit(self, data):
        self.textedit.setText(data)


if __name__ == "__main__":
    _app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    _app.exec()