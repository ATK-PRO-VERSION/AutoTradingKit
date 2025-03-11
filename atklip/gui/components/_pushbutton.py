from PySide6.QtCore import Signal, Qt, QSize, QPoint
from PySide6.QtGui import QIcon, QPainter, QColor
from PySide6.QtWidgets import QPushButton, QWidget

# from atklip.gui.qfluentwidgets.components.dialog_box.color_dialog import ColorDialog
from atklip.app_utils.functions import mkColor
from atklip.gui.qfluentwidgets.components.widgets import ToolButton,SplitDropButton,SplitWidgetBase,\
CardWidget,RoundMenu,PushButton,PrimaryToolButton,ToolTipFilter,ToolTipPosition
from atklip.gui.qfluentwidgets.common import *
from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF, EchangeIcon as EI
from .icon_text_button_ui import  Ui__pushbutton as CIRCLE_ICON_WITH_TEXT_WG
from .iconwidget_with_text_button_ui import  Ui_Form as ICON_WITH_TEXT_WG
from .color_dialog import ColorDialog

class _PushButton(ToolButton):
    """ Transparent push button
    Constructors
    ------------
    * ToolButton(`icon`: QIcon | FluentIcon, `parent`: QWidget = None)
    """
    def __init__(self, *args,**kwargs):
        super().__init__(*args,**kwargs)
        
        self.setIconSize(QSize(20,20))
        self.setFixedHeight(30)
        self.setMinimumWidth(30)
        self.setContentsMargins(2,2,2,2)
        self.setCheckable(True)
        self.setChecked(False)
        color = "transparent"
        self.set_stylesheet(color)
    
    def set_text(self,text,color):
        self.setText(text)
        self.set_stylesheet(color)
    def title(self):
        return self.text()
    def set_stylesheet(self,background_color):
        self.setStyleSheet(f"""QToolButton {{
                        background-color: {background_color};
                        border: none;
                        border-radius: 4px;
                    }}""")
        self.update()
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        self.set_stylesheet(background_color)
        self.setCursor(Qt.CursorShape.ArrowCursor)
        super().enterEvent(event)
    def leaveEvent(self, event):
        color = "transparent"
        self.set_stylesheet(color)
        super().leaveEvent(event)


class BasePushButton(QPushButton):
    """ Transparent push button
    Constructors
    ------------
    * TransparentPushButton(`parent`: QWidget = None)
    * TransparentPushButton(`text`: str, `parent`: QWidget = None, `icon`: QIcon | str | FluentIconBase = None)
    * TransparentPushButton(`icon`: QIcon | FluentIcon, `text`: str, `parent`: QWidget = None)
    """
    def __init__(self,parent:QWidget):
        super().__init__(parent=parent)
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        self.setFixedSize(25,25)
        self.setContentsMargins(2,2,2,2)
    def title(self):
        return self.text()
    def set_stylesheet(self,color):
        self.setStyleSheet(f"""QPushButton {{
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            color: {color};
                            font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial';
                            }}""")
    
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.setStyleSheet(f"""QPushButton {{
            background-color: {background_color};
            border: none;
            border-radius: 4px;
            color: {color};
            font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial';
            }}""")

        #super().enterEvent(event)
    def leaveEvent(self, event):
        #background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        super().leaveEvent(event)



class IconTextChangeButton(QPushButton):
    """ Transparent push button
    Constructors
    ------------
    * TransparentPushButton(`parent`: QWidget = None)
    * TransparentPushButton(`text`: str, `parent`: QWidget = None, `icon`: QIcon | str | FluentIconBase = None)
    * TransparentPushButton(`icon`: QIcon | FluentIcon, `text`: str, `parent`: QWidget = None)
    """
    def __init__(self, icon:FluentIcon=None, text:str="", parent: QWidget=None):
        if text == "":
            super().__init__(parent=parent)
        else:
            super().__init__(text=text, parent=parent)
        self.setCheckable(True)
        self.setChecked(False)
        self._icon = icon
        # self.setIcon(icon)
        # color = self.get_color()
        # self.set_stylesheet(color)
        self.issponsor = False
        self.set_icon_color()
        self.clicked.connect(self.set_icon_color)
        self.setFixedHeight(35)
        self.setMinimumWidth(100)
        self.setMaximumWidth(130)
        
        # self.setContentsMargins(0,0,0,0)
    
    def setIcon(self,icon: FluentIcon|str|QIcon):
        if isinstance(icon,FluentIcon):
            icon = QIcon(icon.path())
        elif isinstance(icon,str):
            icon = QIcon(icon)
        super().setIcon(icon)
    
    def set_text(self,text,color):
        self.setText(text)
        self.set_stylesheet(color)
    def title(self):
        return self.text()
    def set_stylesheet(self,color):
        self.setStyleSheet(f"""QPushButton {{
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            color: {color};
                            font: 15px 'Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial';
                            
                        }}""")
    
    def set_icon_color(self):
        if self.issponsor:
            co_lor = "#f359c9"
            self.set_stylesheet(co_lor)
            return
        else:
            co_lor = "#0055ff"
        if self._icon:
            if self.isChecked():
                _icon = change_svg_color(self._icon.value,co_lor)
                self.setIcon(QIcon(_icon))
            else:
                if isDarkTheme():
                    self.setIcon(self._icon.path(Theme.DARK))
                else:
                    self.setIcon(self._icon.path(Theme.LIGHT))
        # if self.text():
        color = self.get_color()
        self.set_stylesheet(color)
    
    def set_sponsor(self):
        self.issponsor = True
        # _icon = change_svg_color(self._icon.value,"#f359c9")
        # self.setIcon(QIcon(_icon))
        self.set_stylesheet("#f359c9")
      
    def get_color(self):
        if self.issponsor:
            return "#f359c9"
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



class _SplitDropButton(SplitDropButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setIcon(FIF.CHEVRON_RIGHT_MED)
        self.setFixedSize(12,40)
        self.setIconSize(QSize(10, 10))

        self.setStyleSheet("""QToolButton,
                            QToolButton:pressed,
                           QToolButton:checked
                           {
                            border: none;
                            border-radius: 4px;
                            background-color: transparent;}""")
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        self.setStyleSheet(f"""QToolButton,
                            QToolButton:pressed,
                           QToolButton:checked {{
                                    border: none;
                                    border-radius: 4px;
                                    background-color: {background_color};}}""")
        super().enterEvent(event)
    def leaveEvent(self, event):
        self.setStyleSheet("""QToolButton,
                            QToolButton:pressed,
                           QToolButton:checked {
                                    border: none;
                                    border-radius: 4px;
                                    background-color: transparent;}""")
        super().leaveEvent(event)



class ShowmenuButton(SplitWidgetBase):
    """ Split tool button

    Constructors
    ------------
    * SplitToolButton(`parent`: QWidget = None)
    * SplitToolButton(`icon`: QIcon | str | FluentIconBase, `parent`: QWidget = None)
    """

    clicked = Signal()
    @singledispatchmethod
    def __init__(self, parent: QWidget = None):
        super().__init__(parent=parent)
        self.button = _PushButton(self)
        self.button.clicked.connect(self.clicked)
        self.button.clicked.connect(self.set_icon_color)
        #self._fluent_icon:FIF = None
        self.setWidget(self.button)
        self.setDropButton(_SplitDropButton(self))
        self._postInit()
    
    def isChecked(self) -> bool:
        return self.button.isChecked()

    @__init__.register
    def _(self, icon: FluentIconBase, parent: QWidget = None):
        self.__init__(parent)
        self._fluent_icon = icon
        self.setIcon(icon)

    @__init__.register
    def _(self, icon: QIcon, parent: QWidget = None):
        self.__init__(parent)
        self.setIcon(icon)

    @__init__.register
    def _(self, icon: str, parent: QWidget = None):
        self.__init__(parent)
        self.setIcon(icon)

    def change_item(self,icon):
        self._fluent_icon = icon
        _icon = change_svg_color(icon.value,"#0055ff")
        self.button.setIcon(QIcon(_icon))
        self.button.setChecked(True)
        self.parent().parent.uncheck_items(self)
    def setfluentIcon(self,icon):
        self._fluent_icon = icon
        if isDarkTheme():
            icon = self._fluent_icon.path(Theme.DARK)
        else:
            icon = self._fluent_icon.path(Theme.LIGHT)
        self.button.setIcon(icon)
    def set_icon_color(self):
        if self.button.isChecked():
            if self._fluent_icon == None:
                _icon = change_svg_color(self._icon.value,"#0055ff")
                self.button.setIcon(QIcon(_icon))
            else:
                _icon = change_svg_color(self._fluent_icon.value,"#0055ff")
                self.button.setIcon(QIcon(_icon))
        else:
            #print(self.icon)
            if self._fluent_icon == None:
                if isDarkTheme():
                    self.button.setIcon(self._icon.path(Theme.DARK))
                else:
                    self.button.setIcon(self._icon.path(Theme.LIGHT))
            else:
                if isDarkTheme():
                    self.button.setIcon(self._fluent_icon.path(Theme.DARK))
                else:
                    self.button.setIcon(self._fluent_icon.path(Theme.LIGHT))
        self.parent().parent.uncheck_items(self)
    def _postInit(self):
        self.button.setFixedSize(40,40)
        self.button.setIconSize(QSize(30, 30))
        self.dropButton.hide()
    def enterEvent(self, event):
        self.dropButton.show()
        super().enterEvent(event)
    def leaveEvent(self, event):
        self.dropButton.hide()
        super().leaveEvent(event)
    def icon(self):
        return self.button.icon()

    def setIcon(self, icon: Union[QIcon, FluentIconBase, str]):
        self._icon = icon
        self.button.setIcon(icon)

    def setIconSize(self, size: QSize):
        self.button.setIconSize(size)
    
    def setFlyout(self, flyout):
        self.flyout = flyout
    def showFlyout(self):
        """ show flyout """
        w = self.flyout
        if not w:
            return
        # if isinstance(w, RoundMenu):
        w.view.setMinimumWidth(self.width())
        w.view.adjustSize()
        w.adjustSize()
        x = self.width()
        #y = self.height()
        y = 0
        w.show()
        w.move(self.mapToGlobal(QPoint(x, y)))


class ICON_TEXT_BUTTON(CardWidget,ICON_WITH_TEXT_WG):

    def __init__(self,parent:QWidget=None,name:str="",icon:FluentIcon=None):
        super().__init__(parent)
        self.setObjectName(name)
        self._parent = parent
        self.setupUi(self)
        self.parent = parent
        self.items = []
        #_icon  = QIcon(icon.icon_path())
        self.exchange_icon.setIcon(icon)
        self.TitleLabel.setText(name)
        self.clicked.connect(self.onClick)
    def onClick(self):
        #print(self.IconWidget.getIcon(),self.TitleLabel.text())
        self._parent.changePage(self.TitleLabel.text())

class ICON_TEXT_BUTTON_SYMBOL(CardWidget,CIRCLE_ICON_WITH_TEXT_WG):

    def __init__(self,exchange_id,parent:QWidget=None,text:str="",icon:FluentIcon=None):
        super().__init__(parent)
        self._parent = parent
        self.setupUi(self)
        self.setContentsMargins(1,1,1,1)
        self.parent = parent
        self.isChecked = False
        self.items = []
        self.exchange_id = exchange_id
        self.exchange_icon.set_pixmap_icon(icon,30)
        self.TitleLabel.setText(text)
        self.clicked.connect(self.onClick)
    def onClick(self):
        self._parent.changePage(self.exchange_id)

class Color_Picker_Button(PrimaryToolButton):
    """ Color picker button """
    colorChanged = Signal(str)
    def __init__(self, parent=None,color:str="#123232", title: str="", enableAlpha=True):
        super().__init__(parent)
        self.title = title
        self.enableAlpha = enableAlpha
        self.setFixedSize(60, 32)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.color = self.setColor(color)
        self.setCursor(Qt.PointingHandCursor)
        self.clicked.connect(self.showFlyout)
        self.colorChanged.connect(self.setColor,Qt.ConnectionType.AutoConnection)

    def setFlyout(self):
        view = ColorDialog(self.window(),self.colorChanged)
        view.setup_all_btns()
        menu = RoundMenu("Choose color",self)
        menu.addWidget(view)
        self.flyout = menu

    def showFlyout(self):
        """ show flyout """
        self.setFlyout()
        if not self.flyout:
            return

        w = self.flyout

        if isinstance(w, RoundMenu):
            w.view.setMinimumWidth(self.width())
            w.view.adjustSize()
            w.adjustSize()

        dx = w.layout().contentsMargins().left() if isinstance(w, RoundMenu) else 0
        x = -w.width()//2 + dx + self.width()//2
        y = self.height()+5
        w.exec(self.mapToGlobal(QPoint(x, y)))
    

    def __onColorChanged(self, color):
        """ color changed slot """
        self.setColor(color)
        self.colorChanged.emit(color)

    def setColor(self, color):
        """ set color """
        self.color = None
        if isinstance(color,str) or isinstance(color,tuple):
            self.color = mkColor(color)
        elif isinstance(color,QColor):
            self.color = color
        self.update()
        return self.color
    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        pc = QColor(255, 255, 255, 10) if isDarkTheme() else QColor(234, 234, 234)
        painter.setPen(pc)

        if not self.enableAlpha:
            self.color.setAlpha(255)

        painter.setBrush(self.color)
        painter.drawRoundedRect(self.rect().adjusted(1, 1, -1, -1), 5, 5)



class TextButton(PushButton):
    """ Transparent push button
    Constructors
    ------------
    * TransparentPushButton(`parent`: QWidget = None)
    * TransparentPushButton(`text`: str, `parent`: QWidget = None, `icon`: QIcon | str | FluentIconBase = None)
    * TransparentPushButton(`icon`: QIcon | FluentIcon, `text`: str, `parent`: QWidget = None)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        self.setMinimumWidth(40)
        self.setFixedHeight(30)
        self.setContentsMargins(5,5,5,5)
    
    def set_text(self,text,color):
        self.setText(text)
        self.set_stylesheet(color)
    def title(self):
        return self.text()
    def set_stylesheet(self,color):
        self.setStyleSheet(f"""QPushButton {{
                            background-color: transparent;
                            border: none;
                            border-radius: 4px;
                            color: {color};
                            font: 12pt "Segoe UI";
                            font-weight: DemiBold;
                        }}""")
    
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.setStyleSheet(f"""QPushButton {{
            background-color: {background_color};
            border: none;
            border-radius: 4px;
            color: {color};
            font: 12pt "Segoe UI";
            font-weight: DemiBold;
            }}""")

        super().enterEvent(event)
    def leaveEvent(self, event):
        #background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        if self.isChecked():
            color = "#0055ff"
        else:
            color = "#d1d4dc" if isDarkTheme() else  "#161616"
        self.set_stylesheet(color)
        super().leaveEvent(event)


from PySide6.QtCore import QSize, Qt, QRect, QPoint
from PySide6.QtGui import QIcon, QPainter, QImage, QColor, QPixmap
from PySide6.QtWidgets import (QPushButton,
                        )

class CircleICon(QPushButton):
    def __init__(self, parent=None,icon_path="test.svg", size=30): #u":/qfluentwidgets/images/profiles/profile2.png"
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setFixedSize(QSize(size, size))
        # self.setIcon(QIcon(icon_path))
        # self.setIconSize(QSize(size - 10, size - 10))
        self.setFixedHeight(30)
        self.setStyleSheet("""
            QPushButton {
                border: 0px solid;
                border-color: transparent;
                border-radius: %dpx;
                background-color:transparent;
            }
            QPushButton:pressed {
                background-color: #5A5A5A;
            }
        """ % (size // 2))
        
        if icon_path.endswith("png"):
            icon_path = self.crop_and_resize_to_circle(icon_path, size)
        self.set_pixmap_icon(icon_path)

 
    def set_pixmap_icon(self, icon_path):
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(self.width() - 10, self.height() - 10))
    
    def crop_and_resize_to_circle(self,image_path, size):
        image = QImage(image_path)

        # Calculate the crop rectangle
        crop_size = min(image.width(), image.height())
        crop_rect = QRect(
            (image.width() - crop_size) // 2,
            (image.height() - crop_size) // 2,
            crop_size,
            crop_size
        )

        # Crop and resize the image
        cropped_image = image.copy(crop_rect)
        resized_image = cropped_image.scaled(size, size)

        # Create a mask and draw a circle
        mask = QImage(size, size, QImage.Format_Alpha8)
        mask.fill(Qt.transparent)

        painter = QPainter(mask)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(QColor(255, 255, 255))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QPoint(size // 2, size // 2), size // 2, size // 2)
        painter.end()

        # Apply the mask to the resized image
        masked_image = QPixmap(size, size)
        masked_image.fill(Qt.transparent)
        painter.begin(masked_image)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.drawImage(0, 0, resized_image)
        painter.setCompositionMode(QPainter.CompositionMode_DestinationIn)
        painter.drawImage(0, 0, mask)
        painter.end()

        return masked_image                     




class Tradingview_Button(_PushButton):
    """ Transparent toggle tool button

    Constructors
    ------------
    * TransparentToggleToolButton(`parent`: QWidget = None)
    * TransparentToggleToolButton(`icon`: QIcon | str | FluentIconBase, `parent`: QWidget = None)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon:FIF = args[0]
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedSize(40,40)
        self.setIconSize(QSize(30,30))
        self.setContentsMargins(1,1,1,1)
        self.clicked.connect(self.set_icon_color)
        FluentStyleSheet.BUTTON.apply(self)

    def _drawIcon(self, icon, painter, rect):
        if not self.isChecked():
            return ToolButton._drawIcon(self, icon, painter, rect)

        PrimaryToolButton._drawIcon(self, icon, painter, rect, QIcon.On)
    def icon(self):
        return self.icon
    
    def change_status_favorite_btn(self):
        if self.isChecked():
            self.show_favorite_drawtool()
        else:
            self.hide_favorite_drawtool()
    
    def hide_favorite_drawtool(self):
        self.setChecked(False)
        icon_path = FIF.HEART.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
        self.set_icon(icon_path)

    def show_favorite_drawtool(self):
        self.setChecked(True)
        icon_path = FIF.FAVORITE.icon_path()
        self.set_icon(icon_path)


    def set_icon(self, _path):
        icon_path = QIcon(_path)
        self.setIcon(icon_path)

    def set_icon_color(self):
        if self.isChecked():
            _icon = change_svg_color(self.icon.value,"#0055ff")
            self.setIcon(QIcon(_icon))
        else:
            if isDarkTheme():
                self.setIcon(self.icon.path(Theme.DARK))
            else:
                self.setIcon(self.icon.path(Theme.LIGHT))

        if hasattr(self.parent().parent,"uncheck_items"):
            self.parent().parent.uncheck_items(self)

class Lock_Unlock_Button(_PushButton):
    """ Transparent toggle tool button

    Constructors
    ------------
    * TransparentToggleToolButton(`parent`: QWidget = None)
    * TransparentToggleToolButton(`icon`: QIcon | str | FluentIconBase, `parent`: QWidget = None)
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon:FIF = args[0]
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedSize(40,40)
        self.setIconSize(QSize(30,30))
        self.setContentsMargins(1,1,1,1)
        self.clicked.connect(self.set_icon_color)
        FluentStyleSheet.BUTTON.apply(self)

    def _drawIcon(self, icon, painter, rect):
        if not self.isChecked():
            return ToolButton._drawIcon(self, icon, painter, rect)

        PrimaryToolButton._drawIcon(self, icon, painter, rect, QIcon.On)
    def icon(self):
        return self.icon
    
    def change_status_favorite_btn(self):
        if self.isChecked():
            self.show_favorite_drawtool()
        else:
            self.hide_favorite_drawtool()
    
    def hide_favorite_drawtool(self):
        self.setChecked(False)
        icon_path = FIF.HEART.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
        self.set_icon(icon_path)

    def show_favorite_drawtool(self):
        self.setChecked(True)
        icon_path = FIF.FAVORITE.icon_path()
        self.set_icon(icon_path)

    def set_icon(self, _path):
        icon_path = QIcon(_path)
        self.setIcon(icon_path)

    def set_icon_color(self):
        if self.isChecked():
            _icon = change_svg_color(FIF.LOCK.value,"#0055ff")
            self.setIcon(QIcon(_icon))
        else:
            if isDarkTheme():
                self.setIcon(FIF.UNLOCK.path(Theme.DARK))
            else:
                self.setIcon(FIF.UNLOCK.path(Theme.LIGHT))


class Candle_Button(BasePushButton):
    """ Transparent toggle tool button
    Constructors
    ------------
    * TransparentToggleToolButton(`parent`: QWidget = None)
    * TransparentToggleToolButton(`icon`: QIcon | str | FluentIconBase, `parent`: QWidget = None)
    """
    def __init__(self,parent,icon,name):
        super().__init__(parent)

        self.setObjectName(name)
        self.setFixedSize(40,35)
        self.setContentsMargins(5,2,5,2)
        self.setIconSize(QSize(30,30))
        self.setCheckable(True)
        self.setChecked(False)

        self.clicked.connect(self.set_icon_color)

        self._icon:FIF = icon

        self.set_icon_color()
        # self.setToolTipDuration(1000)
        self.installEventFilter(ToolTipFilter(self, 10, ToolTipPosition.TOP))
        self.setToolTip(name)
        FluentStyleSheet.BUTTON.apply(self)

    def set_icon_color(self):
        if self.isChecked():
            _icon = change_svg_color(self._icon.value,"#0055ff")
            self.setIcon(QIcon(_icon))
        else:
            icon_path = self._icon.path(Theme.DARK) if isDarkTheme() else self._icon.path(Theme.LIGHT)
            _icon = QIcon(icon_path)
            self.setIcon(_icon)
            
class Favorite_Draw_Button(BasePushButton):
    """ Transparent toggle tool button

    Constructors
    ------------
    * TransparentToggleToolButton(`parent`: QWidget = None)
    * TransparentToggleToolButton(`icon`: QIcon | str | FluentIconBase, `parent`: QWidget = None)
    """
    def __init__(self, icon:FIF,parent:QWidget):
        super().__init__(parent)
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedSize(40,40)
        self.setIconSize(QSize(25,25))
        self.setContentsMargins(5,5,5,5)
        self.clicked.connect(self.change_status_favorite_btn)
        # self.setToolTipDuration(1000)
        self.installEventFilter(ToolTipFilter(self, 10, ToolTipPosition.RIGHT))
        self.setToolTip("Show/hide favorite draw tools")
        self.change_status_favorite_btn()

    def _drawIcon(self, icon, painter, rect):
        if not self.isChecked():
            return ToolButton._drawIcon(self, icon, painter, rect)
        PrimaryToolButton._drawIcon(self, icon, painter, rect, QIcon.On)

    
    def change_status_favorite_btn(self):
        if self.isChecked():
            self.show_favorite_drawtool()
        else:
            self.hide_favorite_drawtool()
    
    def hide_favorite_drawtool(self):
        self.setChecked(False)
        icon_path = FIF.HEART.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
        self.set_icon(icon_path)

    def show_favorite_drawtool(self):
        self.setChecked(True)
        icon_path = FIF.FAVORITE.icon_path()
        self.set_icon(icon_path)

    def set_icon(self, _path):
        icon_path = QIcon(_path)
        self.setIcon(icon_path)

class Favorite_Button(BasePushButton):
    sig_add_to_favorite = Signal(bool)
    def __init__(self, icon:FIF,parent:QWidget):
        super().__init__(parent)
        self.clicked.connect(self.set_icon_color)
        
        self.setIconSize(QSize(15, 15))
        icon_path = icon.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
        self.set_icon(icon_path)
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedSize(20,20)
        self.setContentsMargins(1,1,1,1)
        # self.button2.setToolTipDuration(-1)  # won't disappear
        self.installEventFilter(ToolTipFilter(self, 10, ToolTipPosition.RIGHT))
        self.setToolTip("add to favorites")
        # self.setToolTipDuration(1000)
        #self.set_icon_color()
    
    def reject_from_favorite(self):
        self.setChecked(False)
        icon_path = FIF.HEART.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
        self.set_icon(icon_path)
        self.hide()
    
    def added_to_favorite(self):
        self.setChecked(True)
        icon_path = FIF.FAVORITE.icon_path()
        self.set_icon(icon_path)
        self.show()
    def set_icon(self, _path):
        icon_path = QIcon(_path)
        self.setIcon(icon_path)
    
    def set_icon_color(self):
        if self.isChecked():
            icon_path = FIF.FAVORITE.icon_path()
            self.set_icon(icon_path)
            self.sig_add_to_favorite.emit(True)
        else:
            icon_path = FIF.HEART.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
            self.set_icon(icon_path)
            self.sig_add_to_favorite.emit(False)

class Help_Button(BasePushButton):
    sig_add_to_favorite = Signal(bool)
    def __init__(self, icon:FIF,parent:QWidget):
        super().__init__(parent)
        self.clicked.connect(self.set_icon_color)
        
        self.setIconSize(QSize(15, 15))
        icon_path = icon.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
        self.set_icon(icon_path)
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedSize(20,20)
        self.setContentsMargins(1,1,1,1)
        # self.button2.setToolTipDuration(-1)  # won't disappear
        self.installEventFilter(ToolTipFilter(self, 10, ToolTipPosition.RIGHT))
        self.setToolTip("What is this, read document!!!")
        # self.setToolTipDuration(1000)
        #self.set_icon_color()
    def reject_from_favorite(self):
        self.setChecked(False)
        icon_path = FIF.HEART.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
        self.set_icon(icon_path)
        self.hide()
    
    def added_to_favorite(self):
        self.setChecked(True)
        icon_path = FIF.FAVORITE.icon_path()
        self.set_icon(icon_path)
        self.show()
    def set_icon(self, _path):
        icon_path = QIcon(_path)
        self.setIcon(icon_path)
    
    def set_icon_color(self):
        if self.isChecked():
            icon_path = FIF.FAVORITE.icon_path()
            self.set_icon(icon_path)
            self.sig_add_to_favorite.emit(True)
        else:
            icon_path = FIF.HEART.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
            self.set_icon(icon_path)
            self.sig_add_to_favorite.emit(False)




class Hide_Show_Button(BasePushButton):
    sig_add_to_favorite = Signal(bool)
    def __init__(self, icon:FIF,parent:QWidget):
        super().__init__(parent)
        self.clicked.connect(self.set_icon_color)
        
        self.setIconSize(QSize(35, 35))
        icon_path = icon.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
        self.set_icon(icon_path)
        self.setCheckable(True)
        self.setChecked(False)
        self.setFixedSize(35,35)
        self.setContentsMargins(0,0,0,0)
        # self.button2.setToolTipDuration(-1)  # won't disappear
        self.installEventFilter(ToolTipFilter(self, 10, ToolTipPosition.RIGHT))
        self.setToolTip("What is this, read document!!!")
        # self.setToolTipDuration(1000)
        #self.set_icon_color()
    def reject_from_favorite(self):
        self.setChecked(False)
        icon_path = FIF.EYE_CLOSE.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
        self.set_icon(icon_path)
        self.hide()
    
    def added_to_favorite(self):
        self.setChecked(True)
        icon_path = FIF.EYE_OPEN.icon_path()
        self.set_icon(icon_path)
        self.show()
    def set_icon(self, _path):
        icon_path = QIcon(_path)
        self.setIcon(icon_path)
    
    def set_icon_color(self):
        if self.isChecked():
            icon_path = FIF.FAVORITE.icon_path()
            self.set_icon(icon_path)
            self.sig_add_to_favorite.emit(True)
        else:
            icon_path = FIF.HEART.path(Theme.DARK) if isDarkTheme() else icon.path(Theme.LIGHT)
            self.set_icon(icon_path)
            self.sig_add_to_favorite.emit(False)