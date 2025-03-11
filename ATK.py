import multiprocessing
import sys
import os
from PySide6.QtCore import QCoreApplication
from PySide6.QtGui import QCloseEvent,QIcon
from PySide6.QtWidgets import QApplication

from atklip.gui.qfluentwidgets.common import setTheme,Theme
from atklip.gui.qfluentwidgets.common.icon import *
from atklip.gui.qfluentwidgets.components.dialog_box import MessageBox
from atklip.gui.views.fluentwindow import WindowBase
from atklip.appmanager.setting.config import cfg
import asyncio

class MainWindow(WindowBase):
    def __init__(self):
        self.isMicaEnabled = False
        super().__init__()

    def closeEvent(self, event: QCloseEvent) -> None:
        quit_msg = QCoreApplication.translate("MainWindow", u"To close window click button OK", None)
        mgsBox = MessageBox("Quit Application?", quit_msg, self.window())
        response = mgsBox.exec()
        if response:
            self.close_window()
            self.deleteLater()
            event.accept()
        else:
            event.ignore()

def main():
    APP_VERSION = "1.0.0"
    APP_NAME = "Auto Trading Kit"
    APP_DISPLAY_NAME = f"ATK (v{APP_VERSION})"
    ORGANIZATION_NAME = "ATK-Team"
    ORGANIZATION_DOMAIN = "ATK.COM"
    ICON_PATH = os.path.join("atklip", "appdata", "appico.ico")

    dpi_scale = cfg.get(cfg.dpiScale)
    if dpi_scale != "Auto":
        os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
        os.environ["QT_SCALE_FACTOR"] = str(dpi_scale)
    
    setTheme(Theme.DARK, True, True)
    app = QApplication(sys.argv + ['--no-sandbox'])
    app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)
    app.setStyle("Fusion")
    app.setApplicationVersion(APP_VERSION)
    app.setApplicationName(APP_NAME)
    app.setApplicationDisplayName(APP_DISPLAY_NAME)
    app.setOrganizationName(ORGANIZATION_NAME)
    app.setOrganizationDomain(ORGANIZATION_DOMAIN) 
    w = MainWindow()
    w.setWindowTitle(f"ATK - {APP_NAME}")
    icon = QIcon(get_real_path(ICON_PATH))
    w.setWindowIcon(icon)
    sys.exit(app.exec())

try: 
    from ctypes import windll # Only exists on Windows.
    myappid = "atkteam.atk.subproduct.version" 
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


if __name__ == '__main__':
    multiprocessing.freeze_support()
    if sys.platform == "darwin" or sys.platform == "linux":
        try:
            import uvloop 
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
        except:
            pass
    else:
        try:
            import winloop 
            winloop.install()
        except:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    main()
    
    