# coding:utf-8
from ctypes import cast
from ctypes.wintypes import LPRECT, MSG
import sys

FramelessMainWindow = None

if sys.platform == "darwin":
    from PySide6.QtWidgets import QMainWindow 
    FramelessMainWindow = QMainWindow
elif sys.platform == "linux":
    # "LINUX"
    from PySide6.QtCore import QCoreApplication, QEvent, Qt, QSize, QRect
    from PySide6.QtWidgets import QWidget, QMainWindow, QDialog

    from qframelesswindow.utils.linux_utils import LinuxMoveResize
    from qframelesswindow.linux.window_effect import LinuxWindowEffect

    class LinuxFramelessWindowBase:
        """ Frameless window base class for Linux system """

        BORDER_WIDTH = 5

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._isSystemButtonVisible = False

        def _initFrameless(self):
            self.windowEffect = LinuxWindowEffect(self)
            self._isResizeEnabled = True

            self.updateFrameless()
            QCoreApplication.instance().installEventFilter(self)


        def updateFrameless(self):
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)


        def setResizeEnabled(self, isEnabled: bool):
            """ set whether resizing is enabled """
            self._isResizeEnabled = isEnabled

        def isSystemButtonVisible(self):
            """ Returns whether the system title bar button is visible """
            return self._isSystemButtonVisible

        def setSystemTitleBarButtonVisible(self, isVisible):
            """ set the visibility of system title bar button, only works for macOS """
            pass

        def systemTitleBarRect(self, size: QSize) -> QRect:
            """ Returns the system title bar rect, only works for macOS

            Parameters
            ----------
            size: QSize
                original system title bar rect
            """
            return QRect(0, 0, size.width(), size.height())

        def eventFilter(self, obj, event):
            et = event.type()
            if et != QEvent.MouseButtonPress and et != QEvent.MouseMove or not self._isResizeEnabled:
                return False

            edges = Qt.Edge(0)
            pos = event.globalPos() - self.pos()
            if pos.x() < self.BORDER_WIDTH:
                edges |= Qt.LeftEdge
            if pos.x() >= self.width()-self.BORDER_WIDTH:
                edges |= Qt.RightEdge
            if pos.y() < self.BORDER_WIDTH:
                edges |= Qt.TopEdge
            if pos.y() >= self.height()-self.BORDER_WIDTH:
                edges |= Qt.BottomEdge

            # change cursor
            if et == QEvent.MouseMove and self.windowState() == Qt.WindowNoState:
                if edges in (Qt.LeftEdge | Qt.TopEdge, Qt.RightEdge | Qt.BottomEdge):
                    self.setCursor(Qt.SizeFDiagCursor)
                elif edges in (Qt.RightEdge | Qt.TopEdge, Qt.LeftEdge | Qt.BottomEdge):
                    self.setCursor(Qt.SizeBDiagCursor)
                elif edges in (Qt.TopEdge, Qt.BottomEdge):
                    self.setCursor(Qt.SizeVerCursor)
                elif edges in (Qt.LeftEdge, Qt.RightEdge):
                    self.setCursor(Qt.SizeHorCursor)
                else:
                    self.setCursor(Qt.ArrowCursor)

            elif obj in (self, self.titleBar) and et == QEvent.MouseButtonPress and edges:
                LinuxMoveResize.starSystemResize(self, event.globalPos(), edges)

            return False

    class LinuxFramelessMainWindow(LinuxFramelessWindowBase, QMainWindow):
        """ Frameless main window for Linux system """

        def __init__(self, parent=None):
            super().__init__(parent=parent)
            self._initFrameless()
    FramelessMainWindow = LinuxFramelessMainWindow

else:
    import win32con
    import win32gui
    from PySide6.QtCore import Qt, QSize, QRect
    from PySide6.QtGui import QCloseEvent, QCursor
    from PySide6.QtWidgets import QApplication, QDialog, QWidget, QMainWindow

    from qframelesswindow.utils import win32_utils as win_utils
    from qframelesswindow.utils.win32_utils import Taskbar
    from qframelesswindow.windows.c_structures import LPNCCALCSIZE_PARAMS
    from qframelesswindow.windows.window_effect import WindowsWindowEffect

    class WindowsFramelessWindowBase:
        """ Frameless window base class for Windows system """

        BORDER_WIDTH = 5

        def __init__(self, parent=None):
            super().__init__(parent)
            self._isSystemButtonVisible = False

        def _initFrameless(self):
            self.windowEffect = WindowsWindowEffect(self)
            self._isResizeEnabled = True
            self.updateFrameless()
            # solve issue #5
            self.windowHandle().screenChanged.connect(self.__onScreenChanged)


        def updateFrameless(self):
            """ update frameless window """
            self.setWindowFlags(self.windowFlags() | Qt.FramelessWindowHint)
            # add DWM shadow and window animation
            self.windowEffect.addWindowAnimation(self.winId())

        def setResizeEnabled(self, isEnabled: bool):
            """ set whether resizing is enabled """
            self._isResizeEnabled = isEnabled

        def isSystemButtonVisible(self):
            """ Returns whether the system title bar button is visible """
            return self._isSystemButtonVisible

        def setSystemTitleBarButtonVisible(self, isVisible):
            """ set the visibility of system title bar button, only works for macOS """
            pass

        def systemTitleBarRect(self, size: QSize) -> QRect:
            """ Returns the system title bar rect, only works for macOS

            Parameters
            ----------
            size: QSize
                original system title bar rect
            """
            return QRect(0, 0, size.width(), size.height())

        def nativeEvent(self, eventType, message):
            """ Handle the Windows message """
            msg = MSG.from_address(message.__int__())
            if not msg.hWnd:
                return False, 0

            if msg.message == win32con.WM_NCHITTEST and self._isResizeEnabled:
                pos = QCursor.pos()
                xPos = pos.x() - self.x()
                yPos = pos.y() - self.y()
                w = self.frameGeometry().width()
                h = self.frameGeometry().height()

                # fixes https://github.com/zhiyiYo/PyQt-Frameless-Window/issues/98
                bw = 0 if win_utils.isMaximized(msg.hWnd) or win_utils.isFullScreen(msg.hWnd) else self.BORDER_WIDTH
                lx = xPos < bw
                rx = xPos > w - bw
                ty = yPos < bw
                by = yPos > h - bw
                if lx and ty:
                    return True, win32con.HTTOPLEFT
                elif rx and by:
                    return True, win32con.HTBOTTOMRIGHT
                elif rx and ty:
                    return True, win32con.HTTOPRIGHT
                elif lx and by:
                    return True, win32con.HTBOTTOMLEFT
                elif ty:
                    return True, win32con.HTTOP
                elif by:
                    return True, win32con.HTBOTTOM
                elif lx:
                    return True, win32con.HTLEFT
                elif rx:
                    return True, win32con.HTRIGHT
            elif msg.message == win32con.WM_NCCALCSIZE:
                if msg.wParam:
                    rect = cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]
                else:
                    rect = cast(msg.lParam, LPRECT).contents

                isMax = win_utils.isMaximized(msg.hWnd)
                isFull = win_utils.isFullScreen(msg.hWnd)

                # adjust the size of client rect
                if isMax and not isFull:
                    ty = win_utils.getResizeBorderThickness(msg.hWnd, False)
                    rect.top += ty
                    rect.bottom -= ty

                    tx = win_utils.getResizeBorderThickness(msg.hWnd, True)
                    rect.left += tx
                    rect.right -= tx

                # handle the situation that an auto-hide taskbar is enabled
                if (isMax or isFull) and Taskbar.isAutoHide():
                    position = Taskbar.getPosition(msg.hWnd)
                    if position == Taskbar.LEFT:
                        rect.top += Taskbar.AUTO_HIDE_THICKNESS
                    elif position == Taskbar.BOTTOM:
                        rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                    elif position == Taskbar.LEFT:
                        rect.left += Taskbar.AUTO_HIDE_THICKNESS
                    elif position == Taskbar.RIGHT:
                        rect.right -= Taskbar.AUTO_HIDE_THICKNESS

                result = 0 if not msg.wParam else win32con.WVR_REDRAW
                return True, result

            return False, 0

        def __onScreenChanged(self):
            hWnd = int(self.windowHandle().winId())
            win32gui.SetWindowPos(hWnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE |
                                win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)


    class WindowsFramelessMainWindow(WindowsFramelessWindowBase, QMainWindow):
        """ Frameless main window for Windows system """

        def __init__(self, parent=None):
            super().__init__(parent=parent)
            self._initFrameless()
    FramelessMainWindow = WindowsFramelessMainWindow

