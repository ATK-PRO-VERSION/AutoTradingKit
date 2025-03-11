
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget, QFrame,QHBoxLayout
from atklip.gui.qfluentwidgets.components import RoundMenu,TitleLabel
from atklip.gui.components import ShowmenuButton,Card_Item
from atklip.gui import FluentIcon as FIF
from atklip.appmanager.setting import AppConfig
from atklip.gui.qfluentwidgets.common import *

class TEXTS(QFrame):
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

        self.splitToolButton = ShowmenuButton(FIF.TEXT,self.parent)
        self.splitToolButton.clicked.connect(self.drawing)
        self.current_tool = None
        self.is_enabled = False
        #create menu
        self.menu = RoundMenu(parent=self)
        self.menu.setFixedWidth(200)
        line_header_wg = QWidget(self.menu)
        headerLayout = QHBoxLayout(line_header_wg)
        line_headerLabel = TitleLabel("TEXT & NOTES")
        line_headerLabel.setFixedHeight(25)
        color = QColor(206, 206, 206) if isDarkTheme() else QColor(0, 0, 0)
        line_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        setFont(line_headerLabel, 13, QFont.DemiBold)
        headerLayout.addWidget(line_headerLabel)
        headerLayout.setContentsMargins(5,0,0,0)
        self.menu.addWidget(line_header_wg)

        self.text = Card_Item(FIF.TEXT,"Text", 'TEXT&NOTES',self)
        # self.anchored_text = Card_Item(FIF.TEXT_ANCHORED,"Anchored Text", 'TEXT&NOTES',self)
        self.note = Card_Item(FIF.NOTE,"Note", 'TEXT&NOTES',self)
        
        # self.anchored_note = Card_Item(FIF.NOTE_ANCHORED,"Anchored Note", 'TEXT&NOTES',self)
        # self.callout = Card_Item(FIF.CALLOUT,"Callout", 'TEXT&NOTES',self)
        # self.comment = Card_Item(FIF.COMMENT,"Comment", 'TEXT&NOTES',self)
        # self.price_label = Card_Item(FIF.PRICE_LABEL,"Price Label", 'TEXT&NOTES',self)
        # self.price_note = Card_Item(FIF.PRICE_NOTE,"Price Note", 'TEXT&NOTES',self)
        # self.signpost = Card_Item(FIF.SIGNPOST,"Signpost", 'TEXT&NOTES',self)
        # self.flag_mark = Card_Item(FIF.FLAG_MARK,"Flag Mark", 'TEXT&NOTES',self)
        # add item to card
        self.text.resize(250, 40)
        self.current_tool =  self.text
        
        self.menu.addWidget(self.text)
        # self.menu.addWidget(self.anchored_text)
        self.menu.addWidget(self.note)
        # self.menu.addWidget(self.anchored_note)
        # self.menu.addWidget(self.callout)
        # self.menu.addWidget(self.comment)
        # self.menu.addWidget(self.price_label)
        # self.menu.addWidget(self.price_note)
        # self.menu.addWidget(self.signpost)
        # self.menu.addWidget(self.flag_mark)
        # split tool button
        self.menu.addSeparator()

        # chanel_header_wg = QWidget(self.menu)
        # chanel_headerLayout = QHBoxLayout(chanel_header_wg)
        # chanel_headerLabel = TitleLabel("CONTENT")
        # chanel_headerLabel.setFixedHeight(25)
        # chanel_headerLabel.setStyleSheet('QLabel{color: '+color.name()+'}')
        # setFont(chanel_headerLabel, 13, QFont.DemiBold)
        # chanel_headerLayout.addWidget(chanel_headerLabel)
        # chanel_headerLayout.setContentsMargins(5,0,0,0)
        # self.menu.addWidget(chanel_header_wg)

        # self.image = Card_Item(FIF.IMAGE,"Image", 'TEXT&NOTES',self)
        # self.idea = Card_Item(FIF.IDEA,"Idea", 'TEXT&NOTES',self)
        # # add item to card
        # # split tool button
        # self.menu.addWidget(self.image)
        # self.menu.addWidget(self.idea)

        
        self.splitToolButton.setFlyout(self.menu)

        self._QLayout.addWidget(self.splitToolButton)
        #self.splitToolButton.dropButton.hide()
        self.map_btn_name:dict = {
            self.text:"draw_text",
            self.note:"draw_note",
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
