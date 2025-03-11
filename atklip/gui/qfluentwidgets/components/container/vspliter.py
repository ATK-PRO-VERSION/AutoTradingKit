from PySide6.QtCore import (Qt)
from PySide6.QtWidgets import (QSplitter,
    QWidget)

class VSplitter(QSplitter):
    def __init__(self, parent:QWidget=None):
        super(VSplitter, self).__init__(Orientation=Qt.Vertical, parent=parent)
        self.setHandleWidth(5)
        self.setObjectName(f"vsplitter_{parent.objectName()}")
        self.setOrientation(Qt.Orientation.Vertical)
        self.setOpaqueResize(True)
        self.setChildrenCollapsible(True)
    def addWidget(self, widget: QWidget) -> None:
        return super().addWidget(widget)