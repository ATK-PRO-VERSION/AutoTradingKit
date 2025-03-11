
from typing import Union
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget

from atklip.gui.qfluentwidgets.components import HWIDGET
from atklip.gui.components import StreamingMode

from atklip.gui.components._pushbutton import IconTextChangeButton

class ModeButton(HWIDGET):
    clicked = Signal()
    def __init__(self,text="Auto-Trading",parent:QWidget=None):
        super().__init__(parent)
        self.setContentsMargins(0,0,0,0)
        self.setFixedHeight(35)
        self.label = StreamingMode(self)
        self.btn = IconTextChangeButton(text=text,parent=self)
        self.addWidget(self.btn)
        self.addWidget(self.label)
        self._is_live = False
        self.btn.clicked.connect(self.on_clicked)
    
    @property
    def is_live(self):
        return self._is_live
    @is_live.setter
    def is_live(self, value):
        self._is_live = value
    
    def set_text(self, text:Union[None,str])->None:
        self.btn.setText(text)
    
    def on_clicked(self)->None:
        self.clicked.emit()
        if self.is_live:
            self.is_live = False
        else:
            self.is_live = True
        self.label.start()