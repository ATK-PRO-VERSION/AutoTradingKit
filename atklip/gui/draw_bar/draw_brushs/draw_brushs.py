
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.qfluentwidgets.components import RoundMenu,TitleLabel
from atklip.gui.components import ShowmenuButton,Card_Item
from atklip.gui import FluentIcon as FIF
from atklip.appmanager.setting import AppConfig
from atklip.gui.qfluentwidgets.common import *
class BRUSHS(QFrame):
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

        self.splitToolButton = ShowmenuButton(FIF.RECTANGLE,self.parent)
        self.splitToolButton.clicked.connect(self.drawing)
        
        self.current_tool = None
        self.is_enabled = False
        #create menu
        self.menu = RoundMenu(parent=self)
        self.menu.setFixedWidth(200)
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(0, 0, 0)
        
        # line_header_wg = QWidget(self.menu)
        # headerLayout = QHBoxLayout(line_header_wg)
        # line_headerLabel = TitleLabel("BRUSHS")
        # line_headerLabel.setFixedHeight(25)
        # line_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        # setFont(line_headerLabel, 13, QFont.DemiBold)
        # headerLayout.addWidget(line_headerLabel)
        # headerLayout.setContentsMargins(5,0,0,0)
        # self.menu.addWidget(line_header_wg)

        # self.brush = Card_Item(FIF.BRUSH,"Brush", 'BRUSHS',self)
        # self.highlighter = Card_Item(FIF.HIGHLIGHTER,"Highlighter", 'BRUSHS',self)

        # # add item to card
        # self.brush.resize(250, 40)
        
        # self.menu.addWidget(self.brush)
        # self.menu.addWidget(self.highlighter)
        # # split tool button
        # self.menu.addSeparator()

        chanel_header_wg = QWidget(self.menu)
        chanel_headerLayout = QHBoxLayout(chanel_header_wg)
        chanel_headerLabel = TitleLabel("ARROWS")
        chanel_headerLabel.setFixedHeight(25)
        chanel_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(chanel_headerLabel, 13, QFont.DemiBold)
        chanel_headerLayout.addWidget(chanel_headerLabel)
        chanel_headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(chanel_header_wg)

        self.arrow_marker = Card_Item(FIF.ARROW_MAKER,"Arrow Marker", 'BRUSHS',self)
        self.arrow = Card_Item(FIF.ARROW,"Arrow", 'BRUSHS',self)
        self.arrow_mark_up = Card_Item(FIF.ARROW_MAKER_UP,"Arrow Mark Up", 'BRUSHS',self)
        self.arrow_mark_down = Card_Item(FIF.ARROW_MAKER_DOWN,"Arrow Mark Down", 'BRUSHS',self)
        
        self.arrow_marker.resize(250, 40)
        # add item to card
        # split tool button
        self.menu.addWidget(self.arrow_marker)
        self.menu.addWidget(self.arrow)
        self.menu.addWidget(self.arrow_mark_up)
        self.menu.addWidget(self.arrow_mark_down)
        self.menu.addSeparator()

        pitchfork_header_wg = QWidget(self.menu)
        pitchfork_headerLayout = QHBoxLayout(pitchfork_header_wg)
        pitchfork_headerLabel = TitleLabel("SHAPES")
        pitchfork_headerLabel.setFixedHeight(25)
        pitchfork_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(pitchfork_headerLabel, 13, QFont.DemiBold)
        pitchfork_headerLayout.addWidget(pitchfork_headerLabel)
        pitchfork_headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(pitchfork_header_wg)

        self.rectangle = Card_Item(FIF.RECTANGLE,"Rectangle", 'BRUSHS',self)
        self.rotated_rectangle = Card_Item(FIF.ROTATE_RECTANGLE,"Rotated Rectangle", 'BRUSHS',self)
        self.path = Card_Item(FIF.PATH,"Path", 'BRUSHS',self)
        self.circle = Card_Item(FIF.CIRCLE,"Circle", 'BRUSHS',self)
        self.elipse = Card_Item(FIF.ELIPSE,"Elipse", 'BRUSHS',self)
        
        
        self.current_tool =  self.rectangle
        
        # self.polyline = Card_Item(FIF.POLIGON,"Polyline", 'BRUSHS',self)
        # self.triangle = Card_Item(FIF.TRIANGLE,"Triangle", 'BRUSHS',self)
        # self.arc = Card_Item(FIF.ARC,"Arc", 'BRUSHS',self)
        # self.curve = Card_Item(FIF.CURVE,"Curve", 'BRUSHS',self)
        # self.double_curve = Card_Item(FIF.DOUBLE_CURVE,"Double Curve", 'BRUSHS',self)
        

        self.menu.addWidget(self.rectangle)
        self.menu.addWidget(self.rotated_rectangle)
        self.menu.addWidget(self.path)
        self.menu.addWidget(self.circle)
        self.menu.addWidget(self.elipse)
        
        # self.menu.addWidget(self.polyline)
        # self.menu.addWidget(self.triangle)
        # self.menu.addWidget(self.arc)
        # self.menu.addWidget(self.curve)
        # self.menu.addWidget(self.double_curve)


        
        self.splitToolButton.setFlyout(self.menu)
        
        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
        self.map_btn_name:dict = {
            self.rectangle:"draw_rectangle",
            self.rotated_rectangle:"draw_rotate_rectangle",
            self.path:"draw_path",
            self.arrow_marker : "draw_arrow_marker",
            self.arrow_mark_up:"draw_up_arrow",
            self.arrow_mark_down:"draw_down_arrow",
            self.arrow:"draw_arrow",
            self.circle:"draw_circle",
            self.elipse:"draw_elipse",
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
