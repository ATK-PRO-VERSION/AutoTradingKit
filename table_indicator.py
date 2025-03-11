# coding: utf-8
import random
import sys
from typing import List, Union

from PySide6.QtCore import Qt, QMargins, QModelIndex, QItemSelectionModel, Property, QRectF,Qt, \
    QAbstractTableModel, QTimer, QModelIndex,QPointF,QPoint,Signal
from PySide6.QtGui import QPainter, QColor, QKeyEvent, QPalette, QBrush, QStandardItemModel,QMouseEvent
from PySide6.QtWidgets import (QStyledItemDelegate, QApplication, QStyleOptionViewItem,QHeaderView,
                             QTableView, QTableWidget, QWidget, QTableWidgetItem, QStyle,QVBoxLayout,
                             QStyleOptionButton)

from atklip.controls.ma_type import IndicatorType
from atklip.gui.qfluentwidgets.components import TableWidget, isDarkTheme, setTheme, Theme, TableView,\
    TableItemDelegate, setCustomStyleSheet,SmoothScrollDelegate\
    ,getFont,themeColor, FluentIcon as FI,ThemeColor, CryptoIcon as CI, EchangeIcon as EI
from atklip.gui.qfluentwidgets.components.widgets.check_box import CheckBoxIcon
from atklip.gui.qfluentwidgets.components.widgets.line_edit import LineEdit
from atklip.gui.qfluentwidgets.components.widgets.label import TitleLabel
from atklip.gui.qfluentwidgets.components.widgets.button import ToolButton


from atklip.gui.qfluentwidgets.common import get_symbol_icon

from atklip.controls.position import Position
from atklip.gui.top_bar.indicator.indicator_table import BasicMenu
     

class RealTimeTable(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Real-Time Update Table Example")
        self.setStyleSheet("""
                           QWidget {
                                border: 1px solid rgba(255, 255, 255, 13);
                                border-radius: 5px;
                                background-color: transparent;
                            }""")
        # Layout chính
        layout = QVBoxLayout()
        
        list_indicators = [IndicatorType.FWMA ,
                                # IndicatorType.ALMA ,
                                IndicatorType.DEMA ,
                                IndicatorType.EMA ,
                                IndicatorType.HMA ,
                                IndicatorType.LINREG ,
                                IndicatorType.MIDPOINT,
                                IndicatorType.PWMA,
                                IndicatorType.RMA ,
                                IndicatorType.SINWMA ,
                                IndicatorType.SMA ,
                                # IndicatorType.SMMA ,
                                IndicatorType.SWMA ,
                                IndicatorType.T3 ,
                                IndicatorType.TEMA ,
                                IndicatorType.TRIMA ,
                                # IndicatorType.VIDYA ,
                                IndicatorType.WMA ,
                                IndicatorType.SSF ,
                                IndicatorType.ZLMA,
                                ]
        
        self.table_view = BasicMenu(self,
                                    sig_add_indicator_to_chart = None,
                                    sig_add_remove_favorite= None,
                                    list_indicators=list_indicators,
                                    _type_indicator="Basic Indicator")
        layout.addWidget(self.table_view)
        self.setLayout(layout)

        # Tạo QTimer để cập nhật dữ liệu theo thời gian thực
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        # self.timer.start(1000)  # Cập nhật mỗi 1 giây

    def update_table(self):
        """Cập nhật dữ liệu của các hàng cụ thể trong bảng."""
        # Ví dụ chỉ cập nhật các hàng 2, 4 và 6
        rows_to_update = [2, 4, 6]
        self.table_view.model().updateRows(rows_to_update)

if __name__ == "__main__":
    setTheme(Theme.DARK,True,True)
    app = QApplication(sys.argv)
    
    window = RealTimeTable()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())

