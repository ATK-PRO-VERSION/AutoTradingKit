
from typing import TYPE_CHECKING
from PySide6.QtGui import QFont,QColor
from PySide6.QtWidgets import QWidget
from atklip.gui.components import Interval_Item
from atklip.gui.qfluentwidgets.components import HWIDGET,HBoxLayout,TitleLabel,RoundMenu
from atklip.gui.qfluentwidgets.common import isDarkTheme,setFont
if TYPE_CHECKING:
    from .btn_interval import IntervalButton
from atklip.appmanager import AppConfig

class INTERVALS(HWIDGET):
    def __init__(self,parent=None,splitToolButton=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent = parent
        self.splitToolButton:IntervalButton = splitToolButton#(self,sig_change_inteval)

        #create menu
        self.menu = RoundMenu(parent=self)
        #self.menu.setFixedWidth(240)
        line_header_wg = QWidget(self.menu)
        headerLayout = HBoxLayout(line_header_wg)
        line_headerLabel = TitleLabel("MINUTES")
        line_headerLabel.setFixedHeight(25)
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(0, 0, 0)
        line_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(line_headerLabel, 13, QFont.DemiBold)
        headerLayout.addWidget(line_headerLabel)
        headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(line_header_wg)
        self.m1 = Interval_Item("1m","1 minute", 'MINUTS',self.splitToolButton)
        self.m3 = Interval_Item("3m","3 minutes", 'MINUTS',self.splitToolButton)
        self.m5 = Interval_Item("5m","5 minutes", 'MINUTS',self.splitToolButton)
        self.m15 = Interval_Item("15m","15 minutes", 'MINUTS',self.splitToolButton)
        self.m30 = Interval_Item("30m","30 minutes", 'MINUTS',self.splitToolButton)
        # add item to card
        self.m1.resize(180, 35)
        
        self.menu.addWidget(self.m1)
        self.menu.addWidget(self.m3)
        self.menu.addWidget(self.m5)
        self.menu.addWidget(self.m15)
        self.menu.addWidget(self.m30)
        # split tool button
        self.menu.addSeparator()

        chanel_header_wg = QWidget(self.menu)
        chanel_headerLayout = HBoxLayout(chanel_header_wg)
        chanel_headerLabel = TitleLabel("HOURS")
        chanel_headerLabel.setFixedHeight(25)
        chanel_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(chanel_headerLabel, 13, QFont.DemiBold)
        chanel_headerLayout.addWidget(chanel_headerLabel)
        chanel_headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(chanel_header_wg)

        self.h1 = Interval_Item("1h","1 hour", 'HOURS',self.splitToolButton)
        self.h2 = Interval_Item("2h","2 hours", 'HOURS',self.splitToolButton)
        self.h4 = Interval_Item("4h","4 hours", 'HOURS',self.splitToolButton)
        self.h6 = Interval_Item("6h","6 hours", 'HOURS',self.splitToolButton)
        self.h12 = Interval_Item("12h","12 hours", 'HOURS',self.splitToolButton)
        # add item to card
        # split tool button
        self.menu.addWidget(self.h1)
        self.menu.addWidget(self.h2)
        self.menu.addWidget(self.h4)
        self.menu.addWidget(self.h6)
        self.menu.addWidget(self.h12)
        self.menu.addSeparator()

        pitchfork_header_wg = QWidget(self.menu)
        pitchfork_headerLayout = HBoxLayout(pitchfork_header_wg)
        pitchfork_headerLabel = TitleLabel("DAY & WEEKS")
        pitchfork_headerLabel.setFixedHeight(25)
        pitchfork_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(pitchfork_headerLabel, 13, QFont.DemiBold)
        pitchfork_headerLayout.addWidget(pitchfork_headerLabel)
        pitchfork_headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(pitchfork_header_wg)

        self.d1 = Interval_Item("1d","1 day", 'DAY & WEEKS',self.splitToolButton)
        self.d3 = Interval_Item("3d","3 days", 'DAY & WEEKS',self.splitToolButton)
        self.w1 = Interval_Item("1w","1 week", 'DAY & WEEKS',self.splitToolButton)

        self.menu.addWidget(self.d1)
        self.menu.addWidget(self.d3)
        self.menu.addWidget(self.w1)
        
        self.splitToolButton.setFlyout(self.menu)
        
        self.addWidget(self.splitToolButton)
 
        self.load_favorites()
    
    def load_favorites(self):
        self.list_old_favorites = AppConfig.get_config_value(f"topbar.interval.favorite")
        if self.list_old_favorites == None:
            AppConfig.sig_set_single_data.emit((f"topbar.interval.favorite",[]))
            self.list_old_favorites = AppConfig.get_config_value(f"topbar.interval.favorite")
        if self.list_old_favorites != []:
            for item_name in self.list_old_favorites:
                item = self.findChild(Interval_Item,item_name)
                if isinstance(item,Interval_Item):
                    item.btn_fovarite.added_to_favorite()
    def enterEvent(self, event):
        #self.splitToolButton.dropButton.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        #self.splitToolButton.dropButton.hide()
        super().leaveEvent(event)
