from PySide6.QtCore import Signal, Qt, QSize, QPoint,QRect
from PySide6.QtGui import QIcon, QPainter, QColor,QImage,QPixmap
from PySide6.QtWidgets import QPushButton, QWidget
from atklip.gui.qfluentwidgets.common.icon import FluentIcon as FIF, EchangeIcon as EI
from atklip.gui.qfluentwidgets.common import isDarkTheme, Theme
from atklip.gui.qfluentwidgets.components.widgets.tool_tip import ToolTipFilter, ToolTipPosition

class ExchangeICon(QPushButton):
    def __init__(self, parent=None,icon_path="test.svg", size=30): #u":/qfluentwidgets/images/profiles/profile2.png"
        super().__init__(parent)
        self.setMouseTracking(True)

        # self.setFixedSize(QSize(size, size))
        # self.setIcon(QIcon(icon_path))
        # self.setIconSize(QSize(size - 10, size - 10))
        #self.setFixedHeight(30)
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
        self.installEventFilter(ToolTipFilter(self, 10, ToolTipPosition.BOTTOM_RIGHT))
        #self.set_pixmap_icon(icon_path)

    def set_pixmap_icon(self, icon_path,size=45):
        if isinstance(icon_path,EI):
            icon_path = icon_path.path()
        elif isinstance(icon_path,FIF):
            icon_path = icon_path.path(Theme.DARK) if isDarkTheme else icon_path.path(Theme.LIGHT)
        if icon_path.endswith("png"):
            icon_path = self.crop_and_resize_to_circle(icon_path, size)
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(size - 10, size - 10))
    
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