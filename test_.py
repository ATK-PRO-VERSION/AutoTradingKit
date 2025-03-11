import sys
from PySide6.QtWidgets import QApplication, QTableView, QMainWindow, QVBoxLayout, QWidget
from PySide6.QtGui import QColor
from PySide6.QtCore import Qt, QAbstractTableModel

class TradingTableModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._headers = ["Trade #", "Type", "Signal", "Date/Time", "Price", "Contracts", "Profit", "Cum. Profit", "Run-up", "Drawdown"]

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self._headers)

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.BackgroundRole:
            if index.column() in [6, 7, 9]:  # Profit, Cum. Profit, Drawdown columns
                value = self._data[index.row()][index.column()]
                if isinstance(value, str) and value.startswith('-'):
                    return QColor(Qt.red)
                else:
                    return QColor(Qt.green)
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._headers[section]
            else:
                return section + 1
        return None

app = QApplication([])

data = [
    [9, "Exit Long", "Open", "", "", "", "-668.50 USD\n-0.72%", "-569.10 USD\n-0.07%", "446.00 USD\n0.48%", "2,173.60 USD\n2.34%"],
    [9, "Entry Long", "buy", "2024-11-16 06:04", "92,821.6 USD", 1, "", "", "", ""],
    [8, "Entry Short", "buy", "2024-11-16 06:04", "92,821.6 USD", 1, "-2,152.10 USD\n-2.37%", "99.40 USD\n-0.21%", "2,651.90 USD\n2.92%", "2,682.40 USD\n2.96%"],
    [8, "Entry Short", "sell", "2024-11-15 01:32", "90,669.5 USD", 1, "", "", "", ""],
    [7, "Exit Long", "sell", "2024-11-15 01:32", "90,669.5 USD", 1, "-1,075.60 USD\n-1.17%", "2,251.50 USD\n-0.11%", "1,605.90 USD\n1.75%", "2,906.00 USD\n3.17%"],
    [7, "Entry Long", "buy", "2024-11-14 11:55", "91,745.1 USD", 1, "", "", "", ""],
    [6, "Exit Short", "buy", "2024-11-14 11:55", "91,745.1 USD", 1, "-453.90 USD\n-0.50%", "3,327.10 USD\n-0.05%", "479.30 USD\n0.53%", "829.40 USD\n0.91%"],
    [6, "Entry Short", "sell", "2024-11-14 05:59", "91,291.2 USD", 1, "", "", "", ""]
]

model = TradingTableModel(data)
view = QTableView()
view.setModel(model)
view.resizeColumnsToContents()

window = QMainWindow()
central_widget = QWidget()
layout = QVBoxLayout(central_widget)
layout.addWidget(view)
window.setCentralWidget(central_widget)
window.resize(1000, 600)
window.show()

app.exec()
