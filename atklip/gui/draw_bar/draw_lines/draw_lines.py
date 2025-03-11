
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.qfluentwidgets.components import RoundMenu,TitleLabel
from atklip.gui.components import ShowmenuButton,Card_Item
from atklip.gui import FluentIcon as FIF
from atklip.appmanager.setting import AppConfig
from atklip.gui.qfluentwidgets.common import *

class LINES(QFrame):
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

        self.splitToolButton = ShowmenuButton(FIF.TRENDLINE,self.parent)
        self.splitToolButton.clicked.connect(self.drawing)
        
        self.current_tool = None
        self.is_enabled = False

        #create menu
        self.menu = RoundMenu(parent=self)
        self.menu.setFixedWidth(200)
        line_header_wg = QWidget(self.menu)
        headerLayout = QHBoxLayout(line_header_wg)
        line_headerLabel = TitleLabel("LINES")
        line_headerLabel.setFixedHeight(25)
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(0, 0, 0)
        line_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(line_headerLabel, 13, QFont.DemiBold)
        headerLayout.addWidget(line_headerLabel)
        headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(line_header_wg)
        self.trend_line = Card_Item(FIF.TRENDLINE,"Trend Line", 'LINE',self)
        # self.ray = Card_Item(FIF.RAY,"Ray", 'LINE',self)
        # self.infor_line = Card_Item(FIF.INFOR_LINE,"Infor Line", 'LINE',self)
        # self.extended_line = Card_Item(FIF.EXTENTED_LINE,"Extended Line", 'LINE',self)
        # self.trend_angle = Card_Item(FIF.TREND_ANGLE,"Trend Angle", 'LINE',self)
        self.horizon_line = Card_Item(FIF.HORIZONTAL_LINE, "Horizontal Line", 'LINE',self)
        self.horizon_ray = Card_Item(FIF.HORIZONTAL_RAY,"Horizontal Ray", 'LINE',self)
        self.vertical_line = Card_Item(FIF.VERTICAL_LINE,"Vertical Line", 'LINE',self)
        # self.cross_line = Card_Item(FIF.CROSS_LINE,"Cross Line", 'LINE',self)
        # add item to card
        self.trend_line.resize(250, 40)
        self.current_tool =  self.trend_line
        
        self.menu.addWidget(self.trend_line)
        # self.menu.addWidget(self.ray)
        # self.menu.addWidget(self.infor_line)
        # self.menu.addWidget(self.extended_line)
        # self.menu.addWidget(self.trend_angle)
        self.menu.addWidget(self.horizon_line)
        self.menu.addWidget(self.horizon_ray)
        self.menu.addWidget(self.vertical_line)
        # self.menu.addWidget(self.cross_line)
        # split tool button
        # self.menu.addSeparator()

        # chanel_header_wg = QWidget(self.menu)
        # chanel_headerLayout = QHBoxLayout(chanel_header_wg)
        # chanel_headerLabel = TitleLabel("CHANELS")
        # chanel_headerLabel.setFixedHeight(25)
        # chanel_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        # setFont(chanel_headerLabel, 13, QFont.DemiBold)
        # chanel_headerLayout.addWidget(chanel_headerLabel)
        # chanel_headerLayout.setContentsMargins(5,0,0,0)
        # self.menu.addWidget(chanel_header_wg)

        # self.parallel_chanel = Card_Item(FIF.PARALLEL_CHANEL,"Parallel Chanel", 'LINE',self)
        # self.regression_trend = Card_Item(FIF.REGRESSION_TREND,"Regression Trend", 'LINE',self)
        # self.flat_top_bottom = Card_Item(FIF.FLAT_TOP_BOTTOM,"Flat Top/Bottom", 'LINE',self)
        # self.disjoint_chanel = Card_Item(FIF.DISJOINT_CHANEL,"Disjoint Chanel", 'LINE',self)
        # add item to card
        # split tool button
        # self.menu.addWidget(self.parallel_chanel)
        # self.menu.addWidget(self.regression_trend)
        # self.menu.addWidget(self.flat_top_bottom)
        # self.menu.addWidget(self.disjoint_chanel)
        # self.menu.addSeparator()

        # pitchfork_header_wg = QWidget(self.menu)
        # pitchfork_headerLayout = QHBoxLayout(pitchfork_header_wg)
        # pitchfork_headerLabel = TitleLabel("PITCHFORKS")
        # pitchfork_headerLabel.setFixedHeight(25)
        # pitchfork_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        # setFont(pitchfork_headerLabel, 13, QFont.DemiBold)
        # pitchfork_headerLayout.addWidget(pitchfork_headerLabel)
        # pitchfork_headerLayout.setContentsMargins(5,0,0,0)
        # self.menu.addWidget(pitchfork_header_wg)

        # self.pitchfork = Card_Item(FIF.PITCHFORK,"Pitchfork", 'LINE',self)
        # self.schiff_pitchfork = Card_Item(FIF.SCHIFF_PITCHFORK,"Schiff Pitchfork", 'LINE',self)
        # self.modify_schiff_pitchfork = Card_Item(FIF.MODIFY_SCHIFF_PITCHFORK,"Modified Schiff Pitchfork", 'LINE',self)
        # self.inside_pitchfork = Card_Item(FIF.INSIDE_PITCHFORK,"Inside Pitchfork", 'LINE',self)

        # self.menu.addWidget(self.pitchfork)
        # self.menu.addWidget(self.schiff_pitchfork)
        # self.menu.addWidget(self.modify_schiff_pitchfork)
        # self.menu.addWidget(self.inside_pitchfork)

        self.splitToolButton.setFlyout(self.menu)
        
        self._QLayout.addWidget(self.splitToolButton)
        
        
        self.map_btn_name:dict = {
            self.trend_line:"draw_trenlines",
            self.horizon_line:"draw_horizontal_line",
            self.horizon_ray:"draw_horizontal_ray",
            self.vertical_line:"draw_verticallines",
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
