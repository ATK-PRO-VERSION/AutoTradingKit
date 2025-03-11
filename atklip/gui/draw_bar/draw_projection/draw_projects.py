
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.qfluentwidgets.components import RoundMenu,TitleLabel
from atklip.gui.components import ShowmenuButton,Card_Item
from atklip.gui import FluentIcon as FIF
from atklip.appmanager.setting import AppConfig
from atklip.gui.qfluentwidgets.common import *
class PROJECTS(QFrame):
    def __init__(self,parent:QWidget=None,sig_draw_object_name=None,sig_add_to_favorite=None):
        super().__init__(parent)
        #self.setClickEnabled(False)
        self.parent = parent
        self.sig_draw_object_name = sig_draw_object_name
        self.sig_add_to_favorite = sig_add_to_favorite
        self.setContentsMargins(0,0,0,0)
        self.setFixedSize(50,40)
        self._QLayout = QHBoxLayout(self)
        self._QLayout.setSpacing(0)
        self._QLayout.setContentsMargins(0, 0, 0, 0)
        self._QLayout.setAlignment(Qt.AlignLeft)

        self.splitToolButton = ShowmenuButton(FIF.PRICE_RANGE,self.parent)
        self.splitToolButton.clicked.connect(self.drawing)
        
        
        self.current_tool = None
        self.is_enabled = False
        #create menu
        self.menu = RoundMenu(parent=self)
        self.menu.setFixedWidth(200)
        line_header_wg = QWidget(self.menu)
        headerLayout = QHBoxLayout(line_header_wg)
        line_headerLabel = TitleLabel("PROJECTION")
        line_headerLabel.setFixedHeight(25)
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(0, 0, 0)
        line_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(line_headerLabel, 13, QFont.DemiBold)
        headerLayout.addWidget(line_headerLabel)
        headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(line_header_wg)
        self.long_position = Card_Item(FIF.LONG_POSITION,"Long Position", 'PROJECTION',self)
        self.short_position = Card_Item(FIF.SHORT_POSITION,"Short Position", 'PROJECTION',self)
        
        # self.forecast = Card_Item(FIF.FORECAST,"Forecast", 'VOLUME-BASED',self)
        # self.bar_pattern = Card_Item(FIF.BAR_PATTERN,"Bar Pattern", 'VOLUME-BASED',self)
        # self.ghost_feed = Card_Item(FIF.SHOST_FEED,"Shost Feed", 'VOLUME-BASED',self)
        # self.projection = Card_Item(FIF.PROJECT, "Projection", 'VOLUME-BASED',self)
       
        # add item to card
        self.long_position.resize(250, 40)
        
        
        self.menu.addWidget(self.long_position)
        self.menu.addWidget(self.short_position)
        
        # self.menu.addWidget(self.forecast)
        # self.menu.addWidget(self.bar_pattern)
        # self.menu.addWidget(self.ghost_feed)
        # self.menu.addWidget(self.projection)

        # split tool button
        self.menu.addSeparator()

        # chanel_header_wg = QWidget(self.menu)
        # chanel_headerLayout = QHBoxLayout(chanel_header_wg)
        # chanel_headerLabel = TitleLabel("VOLUME-BASED")
        # chanel_headerLabel.setFixedHeight(25)
        # chanel_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        # setFont(chanel_headerLabel, 13, QFont.DemiBold)
        # chanel_headerLayout.addWidget(chanel_headerLabel)
        # chanel_headerLayout.setContentsMargins(5,0,0,0)
        # self.menu.addWidget(chanel_header_wg)

        # self.anchored_vwap = Card_Item(FIF.ANCHORED_VWAP,"Anchored VWAP", 'VOLUME-BASED',self)
        # self.fix_range_volume = Card_Item(FIF.FIX_RANGE_VOLUME,"Fixed Range Volume Profile", 'VOLUME-BASED',self)
        # self.anchored_volume = Card_Item(FIF.ANHCHORED_VOLUME,"Anchored Volume Profile", 'VOLUME-BASED',self)
        # # add item to card
        # # split tool button
        # self.menu.addWidget(self.anchored_vwap)
        # self.menu.addWidget(self.fix_range_volume)
        # self.menu.addWidget(self.anchored_volume)
        # self.menu.addSeparator()

        pitchfork_header_wg = QWidget(self.menu)
        pitchfork_headerLayout = QHBoxLayout(pitchfork_header_wg)
        pitchfork_headerLabel = TitleLabel("MEASURER")
        pitchfork_headerLabel.setFixedHeight(25)
        pitchfork_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(pitchfork_headerLabel, 13, QFont.DemiBold)
        pitchfork_headerLayout.addWidget(pitchfork_headerLabel)
        pitchfork_headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(pitchfork_header_wg)

        self.price_range = Card_Item(FIF.PRICE_RANGE,"Price Range", 'MEASURER',self)
        self.date_range = Card_Item(FIF.DATE_RANGE,"Date Range", 'MEASURER',self)
        self.date_price_range = Card_Item(FIF.DATE_PRICE_RANGE,"Date & Price Range", 'MEASURER',self)
      
        self.menu.addWidget(self.price_range)
        self.menu.addWidget(self.date_range)
        self.menu.addWidget(self.date_price_range)
        
        self.current_tool =  self.price_range


        self.splitToolButton.setFlyout(self.menu)

        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
        self.map_btn_name:dict = {
            self.long_position: "draw_long_position",
            self.short_position: "draw_short_position",
            self.price_range:"draw_price_range",
            self.date_range:"draw_date_range",
            self.date_price_range:"draw_date_price_range",
        }
        #self.splitToolButton.dropButton.hide()
    
    def favorite_infor(self,tool_infor):
        tool,icon,is_add = tool_infor[0],tool_infor[1],tool_infor[2]
        self.sig_add_to_favorite.emit((tool.title,icon,self.map_btn_name[tool],is_add))
        
        self.list_favorites:List = AppConfig.get_config_value(f"drawbar.favorite",[])
        tool_infor = {"tool":tool.title,"name":self.map_btn_name[tool],"icon":icon.name}
        if is_add:
            if tool_infor not in self.list_favorites:
                self.list_favorites.append(tool_infor)
        else:
            if tool_infor in self.list_favorites:
                self.list_favorites.remove(tool_infor)
        AppConfig.sig_set_single_data.emit((f"drawbar.favorite",self.list_favorites))
    
    def drawing(self):
        self.sig_draw_object_name.emit((self.current_tool,self.is_enabled,self.map_btn_name[self.current_tool])) 
    
    def set_current_tool(self,tool_infor):
        tool,icon = tool_infor[0],tool_infor[1]
        self.current_tool = tool
        self.splitToolButton.change_item(icon)
        self.set_enable()
        self.sig_draw_object_name.emit((self.current_tool,self.is_enabled,self.map_btn_name[self.current_tool]))
        
        
    def set_enable(self):
        if self.splitToolButton.button.isChecked():
            self.is_enabled = True
        else:
            self.is_enabled = False
    def enterEvent(self, event):
        #self.splitToolButton.dropButton.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        #self.splitToolButton.dropButton.hide()
        super().leaveEvent(event)
