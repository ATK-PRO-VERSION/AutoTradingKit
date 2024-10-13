from multiprocessing.spawn import freeze_support
import signal
import sys
from multiprocessing import Process
import uvicorn
import os

from atklip.gui.qfluentwidgets.common import setTheme,Theme
from atklip.gui.qfluentwidgets.common.icon import *
from atklip.gui.qfluentwidgets.components.dialog_box import MessageBox
from atklip.gui.views.fluentwindow import WindowBase
from PySide6.QtCore import QCoreApplication,QSize
from PySide6.QtGui import QCloseEvent,QIcon
from PySide6.QtWidgets import QApplication


def start_server():
    uvicorn.config.LOOP_SETUPS.update({"winloop":"winloop:install"})
    uvicorn.run("atklip.app_api.sockets:app", 
                host="localhost", 
                port=2022, 
                loop="winloop",
                http="httptools",
                ws="wsproto",
                interface="asgi3",
                lifespan="on",
                workers=1,
                ws_max_queue=1000,
                limit_max_requests=100000,
                timeout_keep_alive=360,
                reload=False)

def create_server():
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
            # os.kill(self.socket_process_pid, signal.SIGTERM)
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