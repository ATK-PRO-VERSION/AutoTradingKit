from typing import TYPE_CHECKING,List
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QAction
from PySide6.QtWidgets import QPushButton, QWidget

from atklip.gui.qfluentwidgets.components.widgets.combo_box import ComboBox
from atklip.gui.qfluentwidgets.common import isDarkTheme
from atklip.gui.qfluentwidgets.components.widgets.menu import MenuAnimationType
from atklip.gui.qfluentwidgets.components.widgets.tool_tip import ToolTipFilter, ToolTipPosition

if TYPE_CHECKING:
    from views.mainlayout import MainWidget


class ReplaySpeed(ComboBox):
    def __init__(self,parent:QWidget=None):
        super(ReplaySpeed,self).__init__(parent)
        self._parent:QWidget = parent
        self.set_values(["0.5x ","1x ","2x ","3x ","5x ","7x "])#,"10x ","15x "
        self.installEventFilter(ToolTipFilter(self, 10, ToolTipPosition.TOP))
        self.setToolTip("Speed update candle")
        self.setCurrentIndex(1)
        color = self.get_color()
        self.set_stylesheet(color)
        self.setFixedSize(35,30)
    
    def set_value(self,value):
        self.setText(str(value))
    def set_values(self,list_item: List[str]):
        self.addItems(list_item)
    def addItems(self, texts):
        for text in texts:
            if isinstance(text,str):
                self.addItem(text)
            elif isinstance(text,tuple):
                self.addItem(text[0],text[1])
    
    def paintEvent(self, e):
        QPushButton.paintEvent(self, e)
      
    def _showComboMenu(self):
        if not self.items:
            return

        menu = self._createComboMenu()
        for item in self.items:
            menu.addAction(QAction(item.icon, item.text))

        # fixes issue #468
        menu.view.itemClicked.connect(lambda i: self._onItemClicked(self.findText(i.text().lstrip())))

        if menu.view.width() < self.width():
            menu.view.setMinimumWidth(self.width())
            menu.adjustSize()

        menu.setMaxVisibleItems(self.maxVisibleItems())
        menu.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        menu.closedSignal.connect(self._onDropMenuClosed)
        self.dropMenu = menu

        # set the selected item
        if self.currentIndex() >= 0 and self.items:
            menu.setDefaultAction(menu.actions()[self.currentIndex()])

        # determine the animation type by choosing the maximum height of view
        x = 0 #self.width() #+ -menu.width()//2 + menu.layout().contentsMargins().left() + self.width()//2
        
        y = self.y() -menu.height() + self.height()/2
                
        pd = self.mapToGlobal(QPoint(x, y))        
        hd = menu.view.heightForAnimation(pd, MenuAnimationType.NONE)

        pu = self.mapToGlobal(QPoint(x, y))
        hu = menu.view.heightForAnimation(pu, MenuAnimationType.NONE)

        print(hd >= hu,hd, hu,pd,pu)
        if hd >= hu:
            # menu.view.adjustSize(pd, MenuAnimationType.NONE)
            menu.exec(pd, aniType=MenuAnimationType.NONE)
        else:
            # menu.view.adjustSize(pu, MenuAnimationType.NONE)
            menu.exec(pu, aniType=MenuAnimationType.NONE)
        # super()._showComboMenu()
    
    
    def set_stylesheet(self,color):
        self.setStyleSheet(f"""QPushButton {{
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            color: {color};
                            font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial';
                        }}""")
         
    def get_color(self):
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        return color
    
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        color = self.get_color()
        self.setStyleSheet(f"""QPushButton {{
            background-color: {background_color};
            border: none;
            border-radius: 4px;
            color: {color};        
            font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial';    
            }}""")
        super().enterEvent(event)
    def leaveEvent(self, event):
        color = self.get_color()
        self.set_stylesheet(color)
        super().leaveEvent(event)


