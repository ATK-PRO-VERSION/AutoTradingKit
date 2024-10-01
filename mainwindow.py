from multiprocessing.spawn import freeze_support
import sys
from multiprocessing import Process, set_start_method
import uvicorn
import os
import signal

from atklip.gui.qfluentwidgets.common import setTheme,Theme
from atklip.gui.qfluentwidgets.common.icon import *
from atklip.gui.qfluentwidgets.components.dialog_box import MessageBox
from atklip.gui.views.fluentwindow import WindowBase
from PySide6.QtCore import QCoreApplication,QSize
from PySide6.QtGui import QCloseEvent,QIcon
from PySide6.QtWidgets import QApplication

# global socket_process, socket_process_pid
# socket_process: Process
# socket_process_pid: int
HTTPProtocolType = Literal["auto", "h11", "httptools"]
WSProtocolType = Literal["auto", "none", "websockets", "wsproto"]
LifespanType = Literal["auto", "on", "off"]
LoopSetupType = Literal["none", "auto", "asyncio", "uvloop"]
InterfaceType = Literal["auto", "asgi3", "asgi2", "wsgi"]

def start_server():
    uvicorn.run("atklip.app_api:app", 
                host="localhost", 
                port=2022, 
                loop="auto",
                http="httptools",
                ws="wsproto",
                workers=1,
                ws_max_queue=1000,
                limit_max_requests=100000,
                reload=False)

def create_server():
    # set_start_method("spawn")
    _socket_process = Process(target=start_server) 
    _socket_process.start()
    process_pid = _socket_process.pid
    return  _socket_process, process_pid

class MainWindow(WindowBase):
    def __init__(self):
        self.isMicaEnabled = False
        self.socket_process,self.socket_process_pid = create_server()
        super().__init__()
    
    def closeEvent(self, event: QCloseEvent) -> None:
        quit_msg = QCoreApplication.translate("MainWindow", u"To close window click button OK", None)   
        mgsBox = MessageBox("Quit Application?", quit_msg, self.window())
        if mgsBox.exec():
            os.kill(self.socket_process_pid, signal.CTRL_BREAK_EVENT)
            self.socket_process.terminate()
            self.socket_process.join()
            self.close_window()
            self.deleteLater()
            event.accept()
        else:
            event.ignore()

def main():
    setTheme(Theme.DARK,True,True)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    app.setApplicationVersion("1.0.0")
    app.setApplicationName('Auto Trading Kit')
    app.setApplicationDisplayName('ATK (v1.0.0)')
    app.setOrganizationName('ATK-Team')
    app.setOrganizationDomain('ATK.COM')
    w = MainWindow()
    w.setWindowTitle('ATK - Auto Trading Kit')
    icon = QIcon()
    app_icon = get_real_path("atklip/appdata")
    icon.addFile(f'{app_icon}/appico.ico',QSize(), QIcon.Normal, QIcon.Off)
    w.setWindowIcon(icon)
    w.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    freeze_support()
    main()