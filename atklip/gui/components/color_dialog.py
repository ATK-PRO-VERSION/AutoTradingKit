
from .color_dialog_ui import Ui_color_picker as ColorWidget

from PySide6.QtWidgets import QWidget
from atklip.gui.qfluentwidgets.common.color import *

from .color_button import ColorButton

class ColorDialog(QWidget,ColorWidget):
    def __init__(self, parent: QWidget | None,colorChanged:None) -> None:
        super(ColorDialog,self).__init__(parent)
        self._parent = parent
        self.setupUi(self)
        self.colorChanged = colorChanged

    def setup_all_btns(self):
        btns = self.children() #self.findChild(ColorButton, "pushButt")
        popular_qcolors = self.get_popular_qcolors()
        list_btns = []
        for btn in btns:
            if isinstance(btn,ColorButton):
                list_btns.append(btn)
                btn.sig_color_out.connect(self.colorChanged)
        _ = zip(list_btns,popular_qcolors)
        for item in _:
            btn = item[0]
            qcolor = item[1]
            btn.set_stylesheet(qcolor)

    def get_popular_qcolors(self,opacity=0):
        popular_colors_rgba = [
            (255, 0, 0, opacity),      # Red
            (0, 255, 0, opacity),      # Green
            (0, 0, 255, opacity),      # Blue
            (255, 255, 0, opacity),    # Yellow
            (0, 255, 255, opacity),    # Cyan
            (255, 0, 255, opacity),    # Magenta
            (255, 165, 0, opacity),    # Orange
            (128, 0, 128, opacity),    # Purple
            (0, 128, 0, opacity),      # Dark Green
            (0, 128, 128, opacity),    # Teal
            (128, 128, 0, opacity),    # Olive
            (128, 0, 0, opacity),      # Maroon
            (128, 128, 128, opacity),  # Gray
            (192, 192, 192, opacity),  # Silver
            (0, 0, 128, opacity),      # Navy
            (255, 192, 203, opacity),  # Pink
            (245, 245, 220, opacity),  # Beige
            (255, 228, 196, opacity),  # Bisque
            (255, 235, 205, opacity),  # Blanched Almond
            (138, 43, 226, opacity),   # Blue Violet
            (165, 42, 42, opacity),    # Brown
            (222, 184, 135, opacity),  # Burly Wood
            (95, 158, 160, opacity),   # Cadet Blue
            (127, 255, 212, opacity),  # Aquamarine
            (210, 105, 30, opacity),   # Chocolate
            (255, 127, 80, opacity),   # Coral
            (100, 149, 237, opacity),  # Cornflower Blue
            (255, 248, 220, opacity),  # Cornsilk
            (220, 20, 60, opacity),    # Crimson
            (0, 255, 255, 128),    # Cyan (Half Transparent)
            (0, 0, 139, opacity),      # Dark Blue
            (0, 139, 139, opacity),    # Dark Cyan
            (184, 134, 11, opacity),   # Dark Golden Rod
            (169, 169, 169, opacity),  # Dark Gray
            (0, 100, 0, opacity),      # Dark Green
            (189, 183, 107, opacity),  # Dark Khaki
            (139, 0, 139, opacity),    # Dark Magenta
            (85, 107, 47, opacity),    # Dark Olive Green
            (255, 140, 0, opacity),    # Dark Orange
            (153, 50, 204, opacity),   # Dark Orchid
            (139, 0, 0, opacity),      # Dark Red
            (233, 150, 122, opacity),  # Dark Salmon
            (143, 188, 143, opacity),  # Dark Sea Green
            (72, 61, 139, opacity),    # Dark Slate Blue
            (47, 79, 79, opacity),     # Dark Slate Gray
            (0, 206, 209, opacity),    # Dark Turquoise
            (148, 0, 211, opacity),    # Dark Violet
            (255, 20, 147, opacity),   # Deep Pink
            (0, 191, 255, opacity),    # Deep Sky Blue
            (105, 105, 105, opacity),  # Dim Gray
            (30, 144, 255, opacity),   # Dodger Blue
            (178, 34, 34, opacity),    # Fire Brick
            (255, 250, 240, opacity),  # Floral White
            (34, 139, 34, opacity),    # Forest Green
            (255, 0, 255, 128),    # Magenta (Half Transparent)
            (220, 220, 220, opacity),  # Gainsboro
            (248, 248, 255, opacity),  # Ghost White
            (255, 215, 0, opacity),    # Gold
            (218, 165, 32, opacity),   # Golden Rod
            # Additional 22 colors
            (240, 248, 255, opacity),  # Alice Blue
            (250, 235, 215, opacity),  # Antique White
            (0, 255, 127, opacity),    # Spring Green
            (255, 69, 0, opacity),     # Orange Red
            (64, 224, 208, opacity),   # Turquoise
            (219, 112, 147, opacity),  # Pale Violet Red
            (255, 239, 213, opacity),  # Papaya Whip
        ]
        #qcolors = [QColor(r, g, b, a) for r, g, b, a in popular_colors_rgba]
        return popular_colors_rgba
        
