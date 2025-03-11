
from PySide6.QtCore import QObject, Signal

class Global_Signal(QObject):
    sig_show_hide_cross = Signal(tuple)
    languge_changed = Signal(str)
    theme_changed = Signal(str)
    custom_theme_changed = Signal(str)
    font_changed = Signal(str)

global global_signal

global_signal = Global_Signal()
