import sys
import time
from PySide6.QtCore import Qt,QRect,QThreadPool,QPoint,QRect,QSize
from PySide6.QtGui import QColor, QPaintEvent,QPen,QFont,QPainter,QMovie
from PySide6.QtWidgets import QWidget, QGraphicsDropShadowEffect,QLabel

from atklip.appmanager.worker import ProcessWorker

class _LoadingProgress(QLabel):
    def __init__(self,parent=None,size=75):
        super().__init__(parent)
        self._parent:QWidget = parent
        self.setStyleSheet("QLabel {background-color: transparent;}")
        # CUSTOM PROPERTIES
        self.setFixedSize(size,size)
        self.setContentsMargins(1,1,1,1)
        self.moviebusy = QMovie(":/qfluentwidgets/images/gif/rainbow.gif")
        self.moviebusy.setBackgroundColor("transparent")
        self.moviebusy.setScaledSize(QSize(size-5,size-5))
        self.setMovie(self.moviebusy)
        #self.moviebusy.stop()
        self.bg_color = 0x44475a
        self.set_shadow()

    def run_process(self,is_show):
        if is_show:
            _x = self._parent.width()
            _y = self._parent.height()
            x = (_x-self.width())/2
            y = (_y-self.height())/2
            self.move(QPoint(x, y))
            if not self.isVisible():
                self.show()
                self.moviebusy.start()
        else:
            self.moviebusy.stop()
            self.hide()
    # ADD DROPSHADOW
    def set_shadow(self):
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)
    def paintEvent(self, arg__1: QPaintEvent) -> None:
        return super().paintEvent(arg__1)

class StreamingMode(QLabel):
    def __init__(self,parent=None,size=35):
        super().__init__(parent)
        self._parent:QWidget = parent
        self.setStyleSheet("QLabel {background-color: transparent;}")
        # CUSTOM PROPERTIES
        self.setFixedSize(size,size)
        self.setContentsMargins(1,1,1,1)
        self.moviebusy = QMovie(":/qfluentwidgets/images/gif/streaming.gif")
        self.moviebusy.setScaledSize(QSize(size-5,size-5))
        self.setMovie(self.moviebusy)
        #self.moviebusy.stop()
        self.is_runing = False
        self.bg_color = 0x44475a
        self.set_shadow()

    def start(self):
        if self.is_runing:
            self.moviebusy.stop()
            self.is_runing = False
            self.hide()
        else:
            self.moviebusy.start()
            self.is_runing = True
            self.show()
    # ADD DROPSHADOW
    def set_shadow(self):
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)


from atklip.gui.qfluentwidgets.components.widgets.progress_ring import IndeterminateProgressRing


class LoadingProgress(IndeterminateProgressRing):
    def __init__(self,parent=None,size=75):
        super().__init__(parent)
        self._parent:QWidget = parent
        self.setStyleSheet("QLabel {background-color: transparent;}")
        # CUSTOM PROPERTIES
        self.setFixedSize(size,size)
        self.setContentsMargins(1,1,1,1)
        #self.moviebusy.stop()
        self.bg_color = 0x44475a
        self.set_shadow()

    def update_pos(self):
        _x = self._parent.width()
        _y = self._parent.height()
        x = (_x-self.width())/2
        y = (_y-self.height())/2
        self.move(QPoint(x, y))
 
    def run_process(self,is_show):
        if is_show:
            _x = self._parent.width()
            _y = self._parent.height()
            x = (_x-self.width())/2
            y = (_y-self.height())/2
            self.move(QPoint(x, y))
            self.start()
            if not self.isVisible():
                self.show()
        else:
            self.stop()
            self.hide()
    # ADD DROPSHADOW
    def set_shadow(self):
        self.shadow = QGraphicsDropShadowEffect(self)
        self.shadow.setBlurRadius(15)
        self.shadow.setXOffset(0)
        self.shadow.setYOffset(0)
        self.shadow.setColor(QColor(0, 0, 0, 80))
        self.setGraphicsEffect(self.shadow)


class CircularProgress(QWidget):
    def __init__(self,parent=None):
        super().__init__(parent)
        self._parent:QWidget = self.parent()
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        # self.setStyleSheet("QWidget {background-color: transparent;}")
        # CUSTOM PROPERTIES
        self.value = 0
        self.width = 75
        self.height = 75
        self.progress_width = 10
        self.progress_rounded_cap = True
        self.max_value = 100
        self.progress_color = 0xff79c6
        # Text
        self.enable_text = False
        self.font_family = "Segoe UI"
        self.font_size = 12
        self.suffix = "%"
        self.text_color = 0xff79c6
        # BG
        self.enable_bg = True
        self.bg_color = 0x44475a
        self.is_running = True
        self.add_shadow(True)
        self.threadpool = QThreadPool(self)

        # SET DEFAULT SIZE WITHOUT LAYOUT
        self.resize(self.width, self.height)

    def run_process(self,is_show):
        if is_show:
            self.is_running = True
            _x = self._parent.width()
            _y = self._parent.height()
            x = (_x-self.width)/2
            y = (_y-self.height)/2
            self.move(QPoint(x, y))
            self.show()
            worker = ProcessWorker(self.loop_set_value)
            worker.signals.sig_process_value.connect(self.set_value)
            worker.signals.finished.connect(self.stop_process)
            worker.start()
        else:
            self.is_running = False

    def loop_set_value(self,sig_process_value, finished):
        value = 0
        while True:
            if not self.is_running:
                finished.emit()
                break
            if value < self.max_value:
                value += 1
            else:
                value = 0
            sig_process_value.emit(value)
            time.sleep(0.01)
        finished.emit()
    def stop_process(self):
        self.hide()

    # ADD DROPSHADOW
    def add_shadow(self, enable):
        if enable:
            self.shadow = QGraphicsDropShadowEffect(self)
            self.shadow.setBlurRadius(15)
            self.shadow.setXOffset(0)
            self.shadow.setYOffset(0)
            self.shadow.setColor("transparent")
            self.setGraphicsEffect(self.shadow)

    # SET VALUE
    def set_value(self, value):
        self.value = value
        self.repaint() # Render progress bar after change value

    # PAINT EVENT (DESIGN YOUR CIRCULAR PROGRESS HERE)
    def paintEvent(self, e):
        # SET PROGRESS PARAMETERS
        width = self.width - self.progress_width
        height = self.height - self.progress_width
        margin = self.progress_width / 2
        value =  self.value * 360 / self.max_value

        # PAINTER
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.Antialiasing) # remove pixelated edges
        paint.setFont(QFont(self.font_family, self.font_size))

        # CREATE RECTANGLE
        # rect = QRect(0, 0, self.width, self.height)
        # paint.setPen(Qt.NoPen)
        # paint.drawRoundedRect(rect,45,45)

        # PEN
        pen = QPen()             
        pen.setWidth(self.progress_width)
        # Set Round Cap
        if self.progress_rounded_cap:
            pen.setCapStyle(Qt.RoundCap)

        # ENABLE BG
        if self.enable_bg:
            pen.setColor(QColor(self.bg_color))
            paint.setPen(pen)  
            paint.drawArc(margin, margin, width, height, 0, 360 * 16) 

        # CREATE ARC / CIRCULAR PROGRESS
        pen.setColor(QColor(self.progress_color))
        paint.setPen(pen)      
        paint.drawArc(margin, margin, width, height, -90 * 16, -value * 16)       

        # # CREATE TEXT
        # if self.enable_text:
        #     pen.setColor(QColor(self.text_color))
        #     paint.setPen(pen)
        #     paint.drawText(rect, Qt.AlignCenter, f"{self.value}{self.suffix}")          

        # END
        paint.end()

