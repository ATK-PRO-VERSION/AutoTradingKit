
from typing import Union
from PySide6.QtCore import QSize

from atklip.gui.components._pushbutton import IconTextChangeButton


class ReplayButton(IconTextChangeButton):
    def __init__(self,icon, text, parent):
        super().__init__(icon, text, parent)
        self.setObjectName("btn_replay")
        self.setIconSize(QSize(30, 30))
        
    def set_text(self, text:Union[None,str])->None:
        if isinstance(text, str):
            raise TypeError("Cannot set text for a SymbolButton")
        super().setText(text)
        
    def icon(self):
        return super().icon()
    

