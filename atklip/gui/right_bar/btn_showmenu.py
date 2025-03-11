from PySide6.QtCore import Signal, QSize, QPoint
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget
from atklip.gui.qfluentwidgets.components import SplitDropButton,ToolButton,SplitWidgetBase,SplitWidgetBase,RoundMenu
from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF
from atklip.gui.qfluentwidgets.common import *

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


class _PushButton(ToolButton):
    """ Transparent push button
    Constructors
    ------------
    * TransparentPushButton(`parent`: QWidget = None)
    * TransparentPushButton(`text`: str, `parent`: QWidget = None, `icon`: QIcon | str | FluentIconBase = None)
    * TransparentPushButton(`icon`: QIcon | FluentIcon, `text`: str, `parent`: QWidget = None)
    """
    def __init__(self, *args,**kwargs):
        #_icon = QIcon(icon.path())
        super().__init__(*args,**kwargs)
        color = "transparent"
        self.set_stylesheet(color)
        self.setIconSize(QSize(30,30))
        self.setFixedHeight(30)
        self.setMinimumWidth(120)
        self.setContentsMargins(2,2,2,2)
        self.setObjectName('ShowmenuButton')
        self.setCheckable(True)
        self.setChecked(False)
    
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
    def enterEvent(self, event):
        background_color = "rgba(255, 255, 255, 0.0837)" if isDarkTheme() else "#9b9b9b"
        self.set_stylesheet(background_color)
        super().enterEvent(event)
    def leaveEvent(self, event):
        color = "transparent"
        self.set_stylesheet(color)
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
        self.button.setIconSize(QSize(35, 35))
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
        if isinstance(w, RoundMenu):
            w.view.setMinimumWidth(self.width())
            w.view.adjustSize()
            w.adjustSize()
            x = self.width()
            #y = self.height()
            y = 0
            w.exec(self.mapToGlobal(QPoint(x, y)))