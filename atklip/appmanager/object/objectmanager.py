from PySide6.QtCore import QObject, Signal
from PySide6.QtGui import QFont
from PySide6.QtWidgets import QWidget

class ObjectManager(QObject):
    object_added = Signal(object)
    object_removed = Signal(object)

    def __init__(self):
        super().__init__()
        self.objects = []

    def widget_update_stylesheet(self,widget):
        widget.update_stylesheet()

    def setFont(self,widget: QWidget, fontSize=14, weight=QFont.Normal):
        """ set the font of widget
        Parameters
        ----------
        widget: QWidget
            the widget to set font

        fontSize: int
            font pixel size
        weight: `QFont.Weight`
            font weight
        """
        widget.setFont(self.getFont(fontSize, weight))
        widget.update()

    def getFont(self,fontSize=14, weight=QFont.Normal):
        """ create font

        Parameters
        ----------
        fontSize: int
            font pixel size

        weight: `QFont.Weight`
            font weight
        """
        font = QFont()
        font.setFamilies(['Segoe UI', 'Microsoft YaHei', 'PingFang SC',  'Arial'])
        font.setPixelSize(fontSize)
        font.setWeight(weight)
        return font

    def get_all_element(self):
        return 

    def add_object(self, obj):
        if obj not in self.objects:
            self.objects.append(obj)
            self.object_added.emit(obj)

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)
            self.object_removed.emit(obj)

    def get_objects(self):
        return self.objects