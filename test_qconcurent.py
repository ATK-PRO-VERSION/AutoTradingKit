from PySide6.QtWidgets import QApplication, QWidget
from PySide6.QtGui import QPainter, QPolygon, QColor, QBrush
from PySide6.QtCore import QPoint, Qt
import sys

class ArrowWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Arrow Up and Down Example")
        self.setGeometry(100, 100, 600, 400)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Tạo màu cho mũi tên
        painter.setBrush(QBrush(QColor("blue")))
        painter.setPen(Qt.NoPen)  # Không có đường viền

        # Kích thước mũi tên
        tail_width = 20
        tail_length = 80
        triangle_width = 40
        triangle_length = 40

        # Vẽ mũi tên hướng lên trên
        self.draw_arrow_up(painter, 150, 300, tail_width, tail_length, triangle_width, triangle_length)

        # Vẽ mũi tên hướng xuống dưới
        self.draw_arrow_down(painter, 450, 100, tail_width, tail_length, triangle_width, triangle_length)

    def draw_arrow_up(self, painter, x, y, tail_width, tail_length, triangle_width, triangle_length):
        """
        Vẽ mũi tên hướng lên trên tại vị trí (x, y).
        - x, y: Tọa độ của phần dưới của mũi tên.
        """
        # Vẽ đuôi mũi tên (hình chữ nhật)
        painter.drawRect(x - tail_width // 2, y - tail_length, tail_width, tail_length)

        # Vẽ đầu mũi tên (hình tam giác hướng lên trên)
        points = QPolygon([
            QPoint(x, y - tail_length - triangle_length),    # Đỉnh nhọn của tam giác
            QPoint(x - triangle_width // 2, y - tail_length),  # Góc trái
            QPoint(x + triangle_width // 2, y - tail_length)   # Góc phải
        ])
        painter.drawPolygon(points)

    def draw_arrow_down(self, painter, x, y, tail_width, tail_length, triangle_width, triangle_length):
        """
        Vẽ mũi tên hướng xuống dưới tại vị trí (x, y).
        - x, y: Tọa độ của phần trên của mũi tên.
        """
        # Vẽ đuôi mũi tên (hình chữ nhật)
        painter.drawRect(x - tail_width // 2, y, tail_width, tail_length)

        # Vẽ đầu mũi tên (hình tam giác hướng xuống dưới)
        points = QPolygon([
            QPoint(x, y + tail_length + triangle_length),    # Đỉnh nhọn của tam giác
            QPoint(x - triangle_width // 2, y + tail_length),  # Góc trái
            QPoint(x + triangle_width // 2, y + tail_length)   # Góc phải
        ])
        painter.drawPolygon(points)

if __name__ == "__main__":
    app = QApplication(sys.argv)

    window = ArrowWidget()
    window.show()

    sys.exit(app.exec())
