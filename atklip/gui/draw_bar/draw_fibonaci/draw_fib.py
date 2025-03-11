
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.qfluentwidgets.components import RoundMenu,TitleLabel
from atklip.gui.components import ShowmenuButton,Card_Item
from atklip.gui import FluentIcon as FIF
from atklip.appmanager.setting import AppConfig
from atklip.gui.qfluentwidgets.common import *

class FIBONACCI(QFrame):
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

        self.splitToolButton = ShowmenuButton(FIF.FIB_RETRACEMENT,self.parent)
        self.splitToolButton.clicked.connect(self.drawing)
        
        self.current_tool = None
        self.is_enabled = False
        #create menu
        self.menu = RoundMenu(parent=self)
        self.menu.setFixedWidth(200)
        line_header_wg = QWidget(self.menu)
        headerLayout = QHBoxLayout(line_header_wg)
        line_headerLabel = TitleLabel("FIBONACCI")
        line_headerLabel.setFixedHeight(25)
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(0, 0, 0)
        line_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(line_headerLabel, 13, QFont.DemiBold)
        headerLayout.addWidget(line_headerLabel)
        headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(line_header_wg)
        self.fib_retracement = Card_Item(FIF.FIB_RETRACEMENT,"Fib Retracement", 'FIBONACCI',self)
        self.fib_retracement_2 = Card_Item(FIF.FIB_RETRACEMENT,"Fib Retracement 2", 'FIBONACCI',self)
        self.risk_reward_ratio = Card_Item(FIF.FIB_RETRACEMENT,"Risk Reward Ratio", 'FIBONACCI',self)
        
        # self.fib_trend_base = Card_Item(FIF.FIB_TREND_BASE,"Trend-Based Fib Extension", 'FIBONACCI',self)
        # self.fib_chanel = Card_Item(FIF.FIB_CHANEL,"Fib Chanel", 'FIBONACCI',self)
        # self.fib_timezone = Card_Item(FIF.FIB_TIMEZONE,"Fib TimeZone", 'FIBONACCI',self)
        # self.fib_speed_resistance = Card_Item(FIF.FIB_SPEED_RESISTANCE,"Fib Speed Resistance Fan", 'FIBONACCI',self)
        # self.fib_trendbase_time = Card_Item(FIF.FIB_TRENDBASE_TIME, "Trend-Based Fib Time", 'FIBONACCI',self)
        # self.fib_circle = Card_Item(FIF.FIB_CIRCLE,"Fib Circle", 'FIBONACCI',self)
        # self.fib_spiral = Card_Item(FIF.FIB_SPIRAL,"Fib Spriral", 'FIBONACCI',self)
        # self.fib_restracement_arcs = Card_Item(FIF.FIB_RETRACEMENTS_ARCS,"Fib Speed Resistance Arcs", 'FIBONACCI',self)
        # self.fib_wedge = Card_Item(FIF.FIB_WEDGE,"Fib Wedge", 'FIBONACCI',self)
        # self.pitchfan = Card_Item(FIF.PITCHFAN,"Pitfan", 'FIBONACCI',self)

        # add item to card
        self.fib_retracement.resize(250, 40)
        
        self.current_tool =  self.fib_retracement
        
        self.menu.addWidget(self.fib_retracement)
        self.menu.addWidget(self.fib_retracement_2)
        self.menu.addWidget(self.risk_reward_ratio)
        
        # self.menu.addWidget(self.fib_trend_base)
        # self.menu.addWidget(self.fib_chanel)
        # self.menu.addWidget(self.fib_timezone)
        # self.menu.addWidget(self.fib_speed_resistance)
        # self.menu.addWidget(self.fib_trendbase_time)
        # self.menu.addWidget(self.fib_circle)
        # self.menu.addWidget(self.fib_spiral)
        # self.menu.addWidget(self.fib_restracement_arcs)
        # self.menu.addWidget(self.fib_wedge)
        # self.menu.addWidget(self.pitchfan)
        # split tool button
        # self.menu.addSeparator()

        # chanel_header_wg = QWidget(self.menu)
        # chanel_headerLayout = QHBoxLayout(chanel_header_wg)
        # chanel_headerLabel = TitleLabel("GANN")
        # chanel_headerLabel.setFixedHeight(25)
        # chanel_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        # setFont(chanel_headerLabel, 13, QFont.DemiBold)
        # chanel_headerLayout.addWidget(chanel_headerLabel)
        # chanel_headerLayout.setContentsMargins(5,0,0,0)
        # self.menu.addWidget(chanel_header_wg)

        # self.gan_box = Card_Item(FIF.GAN_BOX,"Gann Box", 'FIBONACCI',self)
        # #self.gan_squre_fix = Card_Item(FIF.GAN_SQUARE_FIX,"Gann Square Fixed", '',self)
        # self.gan_square = Card_Item(FIF.GAN_SQUARE,"Gann Square", 'FIBONACCI',self)
        # self.gan_fan = Card_Item(FIF.GAN_FAN,"Gann Fan", 'FIBONACCI',self)
        # # add item to card
        # # split tool button
        # self.menu.addWidget(self.gan_box)
        # #self.menu.addWidget(self.gan_squre_fix)
        # self.menu.addWidget(self.gan_square)
        # self.menu.addWidget(self.gan_fan)

        self.splitToolButton.setFlyout(self.menu)

        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
        self.map_btn_name:dict = {
            self.fib_retracement:"draw_fib_retracement",
            self.fib_retracement_2:"draw_fib_retracement_2",
            self.risk_reward_ratio:"draw_risk_reward_ratio"
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
