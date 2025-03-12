import sys
from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtCore import Qt

class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Ví dụ PySide6")
        self.setGeometry(100, 100, 400, 300)

    def mousePressEvent(self, event):
        # Lấy vị trí chuột bằng position()
        mouse_position = event.position()
        print(f"Bạn đã nhấn chuột tại: {mouse_position}")

        # Kiểm tra nút chuột
        if event.button() == Qt.LeftButton:
            print("Bạn đã nhấn nút trái chuột")
        elif event.button() == Qt.RightButton:
            print("Bạn đã nhấn nút phải chuột")
        super().mousePressEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = MyWindow()
    window.show()

    sys.exit(app.exec())