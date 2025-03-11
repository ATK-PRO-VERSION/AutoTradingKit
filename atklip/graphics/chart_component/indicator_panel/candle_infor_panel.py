from PySide6.QtWidgets import QWidget, QHBoxLayout, QTextEdit
from PySide6.QtGui import Qt
from atklip.graphics.chart_component.globarvar import global_signal
class CandlePanel(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setStyleSheet("""background-color: transparent; color:#eaeaea; font: bold 14px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial';
                            """)
        
        self.setFixedSize(320, 25)
        #self.move(300, 0)
        # self.
        layout = QHBoxLayout(self)
        self.setLayout(layout)
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        self.candle_info = QTextEdit(self)
        self.candle_info.setContentsMargins(0,0,0,0)
        self.candle_info.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        layout.addWidget(self.candle_info)
        
        # layout.addWidget(self.main_sub_zigzag)
    def loading(self):
        self.moviebusy.start()
    def stopload(self):
        self.moviebusy.stop()
    def enterEvent(self, ev):
        global_signal.sig_show_hide_cross.emit((False,None))
        super().enterEvent(ev)
    def leaveEvent(self, ev):
        super().leaveEvent(ev)