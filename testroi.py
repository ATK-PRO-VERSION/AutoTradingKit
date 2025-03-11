import sys
from PySide6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QFileDialog, QScrollArea
from PySide6.QtGui import QPixmap
from pdf2image import convert_from_path
from PIL.ImageQt import ImageQt

class PDFViewer(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("PDF Viewer")
        self.setGeometry(100, 100, 800, 600)

        # Create a scroll area to display PDF pages
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)

        # Create a container widget for the scroll area
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.scroll_area.setWidget(self.container)

        # Set the central widget
        self.setCentralWidget(self.scroll_area)

        # Open a PDF file
        self.openPDF()

    def openPDF(self):
        # Open a file dialog to select a PDF file
        file_path, _ = QFileDialog.getOpenFileName(self, "Open PDF File", "", "PDF Files (*.pdf)")

        if file_path:
            # Convert PDF pages to images
            images = convert_from_path(file_path,size=(800,1000))

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    viewer = PDFViewer()
    viewer.show()
    sys.exit(app.exec())