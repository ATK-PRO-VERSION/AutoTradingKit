from multiprocessing.spawn import freeze_support
import sys
from multiprocessing import Process
import uvicorn

from atklip.gui.qfluentwidgets.common import setTheme,Theme
from atklip.gui.qfluentwidgets.common.icon import *
from atklip.gui.qfluentwidgets.components.dialog_box import MessageBox
from atklip.gui.views.fluentwindow import WindowBase
from PySide6.QtCore import QCoreApplication,QSize
from PySide6.QtGui import QCloseEvent,QIcon
from PySide6.QtWidgets import QApplication

global socket_process
socket_process: Process

class MainWindow(WindowBase):
    def __init__(self):
        self.isMicaEnabled = False
        super().__init__()
    
    def closeEvent(self, event: QCloseEvent) -> None:
        quit_msg = QCoreApplication.translate("MainWindow", u"To close window click button OK", None)   
        mgsBox = MessageBox("Quit Application?", quit_msg, self.window())
        if mgsBox.exec():
            socket_process.terminate()
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

def create_server():
    _socket_process = Process(target=uvicorn.run, kwargs={
                                                "app": "atklip.app_api_socket:app", 
                                                "host": "localhost",
                                                "port": 2022,
                                                "ws_max_queue":1000,
                                                "limit_max_requests":100000,
                                                "reload": False
                                                }) #"workers": 2,# "reload":True
    _socket_process.start()
    return  _socket_process


if __name__ == '__main__':
    freeze_support()
    socket_process = create_server()
    main()