import sys
from atklip.gui.qfluentwidgets.common.icon import get_real_path
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QScrollArea
from PySide6.QtGui import QPixmap
from pdf2image import convert_from_path
from PIL.ImageQt import ImageQt

class ReadmeViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Readme Viewer")
        self.setWindowIcon(self.window().windowIcon())
        # Create a scroll area to display PDF pages

        self.vlayout = QVBoxLayout(self)
        self.vlayout.setContentsMargins(0,0,0,0)
        
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # Create a container widget for the scroll area
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.layout.setContentsMargins(0,0,0,0)
        self.scroll_area.setWidget(self.container)

        # Set the central widget
        self.setLayout(self.vlayout)

        self.vlayout.addWidget(self.scroll_area)

        readme_path:str = get_real_path("atklip/appdata/readme.pdf")

        if sys.platform == "win32":
            images = convert_from_path(readme_path,size=(800,1000),poppler_path="bin")
        else:
            images = convert_from_path(readme_path,size=(800,1000))
        # Clear previous content
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
        # Display each page as an image in a QLabel
        for image in images:
            qimage = ImageQt(image)
            pixmap = QPixmap.fromImage(qimage)
            pixmap.scaledToWidth(800)
            pixmap.scaledToHeight(600)
            label = QLabel(self)
            label.setPixmap(pixmap)
            self.layout.addWidget(label)
    def show(self):
        desktop = QApplication.screens()[0].availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.resize(800, 800)
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)
        return super().show()
