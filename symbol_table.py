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

from atklip.appmanager.setting.config import AppConfig
from atklip.gui.qfluentwidgets.common.icon import get_exchange_icon
from atklip.gui.qfluentwidgets.components import TableWidget, isDarkTheme, setTheme, Theme, TableView,\
    TableItemDelegate, setCustomStyleSheet,SmoothScrollDelegate\
    ,getFont,themeColor, FluentIcon as FI,ThemeColor, CryptoIcon as CI, EchangeIcon as EI
from atklip.gui.qfluentwidgets.components.widgets.check_box import CheckBoxIcon
from atklip.gui.qfluentwidgets.components.widgets.line_edit import LineEdit
from atklip.gui.qfluentwidgets.components.widgets.label import TitleLabel
from atklip.gui.qfluentwidgets.components.widgets.button import ToolButton


from atklip.gui.qfluentwidgets.common import get_symbol_icon

from atklip.controls.position import Position


class PositionItemDelegate(QStyledItemDelegate):

    def __init__(self, parent: QTableView):
        super().__init__(parent)
        self.margin = 2
        self.hoverRow = -1
        self.pressedRow = -1
        self.mouse_pos:QPointF|QPoint = None
        self.selectedRows = set()
        self.on_favorite_btn = False
        self.data = parent.data
        

    def setHoverRow(self, row: int):
        self.hoverRow = row

    def setPressedRow(self, row: int):
        self.pressedRow = row

    def setSelectedRows(self, indexes: List[QModelIndex]):
        self.selectedRows.clear()
        for index in indexes:
            self.selectedRows.add(index.row())
            if index.row() == self.pressedRow:
                self.pressedRow = -1

    def sizeHint(self, option, index):
        # increase original sizeHint to accommodate space needed for border
        size = super().sizeHint(option, index)
        size = size.grownBy(QMargins(0, self.margin, 0, self.margin))
        return size

    def createEditor(self, parent: QWidget, option: QStyleOptionViewItem, index: QModelIndex) -> QWidget:
        lineEdit = TitleLabel(parent)
        # lineEdit = LineEdit(parent)
        lineEdit.setProperty("transparent", False)
        lineEdit.setStyle(QApplication.style())
        lineEdit.setText(option.text)
        return lineEdit
    
    def updateEditorGeometry(self, editor: QWidget, option: QStyleOptionViewItem, index: QModelIndex):
        rect = option.rect
        y = rect.y() + (rect.height() - editor.height()) // 2
        x, w = max(8, rect.x()), rect.width()
        if index.column() == 0:
            w -= 8

        editor.setGeometry(x, y, w, rect.height())

    def initStyleOption(self, option: QStyleOptionViewItem, index: QModelIndex):
        super().initStyleOption(option, index)
        
        # if index.column() == 2:
        #     option.displayAlignment = Qt.AlignLeft
        # elif index.column() == 3:
        #     option.displayAlignment = Qt.AlignRight
  
        # font
        option.font = index.data(Qt.FontRole) or getFont(13)
        # text color
        textColor = Qt.white if isDarkTheme() else Qt.black
        textBrush = index.data(Qt.ForegroundRole)   # type: QBrush
        if textBrush is not None:
            textColor = textBrush.color()

        option.palette.setColor(QPalette.Text, textColor)
        option.palette.setColor(QPalette.HighlightedText, textColor)

    def paint(self, painter, option, index):
        painter.save()
        painter.setPen(Qt.NoPen)
        painter.setRenderHint(QPainter.Antialiasing)

        # set clipping rect of painter to avoid painting outside the borders
        painter.setClipping(True)
        painter.setClipRect(option.rect)

        # call original paint method where option.rect is adjusted to account for border
        option.rect.adjust(0, self.margin, 0, -self.margin)

        # draw highlight background
        isHover = self.hoverRow == index.row()
        isPressed = self.pressedRow == index.row()
        
        
        
        isAlternate = index.row() % 2 == 0 and self.parent().alternatingRowColors()
        isDark = isDarkTheme()

        c = 255 if isDark else 0
        alpha = 0

        if index.row() not in self.selectedRows:
            if isPressed:
                alpha = 9 if isDark else 6
            elif isHover:
                alpha = 12
            elif isAlternate:
                alpha = 5
        else:
            if isPressed:
                alpha = 15 if isDark else 9
            elif isHover:
                alpha = 25
            else:
                alpha = 17
 
        if index.data(Qt.ItemDataRole.BackgroundRole):
            painter.setBrush(index.data(Qt.ItemDataRole.BackgroundRole))
        else:
            painter.setBrush(QColor(c, c, c, alpha))

        self._drawBackground(painter, option, index)
        # draw indicator
        if index.column() == 1:
                self._drawTokenIcon(painter, option, index)
        elif index.column() == 4:
                self._drawExchangeIcon(painter, option, index)
        elif index.column() == 0:
            self._drawFavorite(painter, option, index)
        
        painter.restore()
        super().paint(painter, option, index)

    def _drawBackground(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
        """ draw row background """
        r = 5
        if index.column() == 0:
            rect = option.rect.adjusted(4, 0, r + 1, 0)
            painter.drawRoundedRect(rect, r, r)
        elif index.column() == index.model().columnCount(index.parent()) - 1:
            rect = option.rect.adjusted(-r - 1, 0, -4, 0)
            painter.drawRoundedRect(rect, r, r)
        else:
            rect = option.rect.adjusted(-1, 0, 1, 0)
            painter.drawRect(rect)
    
    def _drawFavorite(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
         # Lấy trạng thái check (nếu cần)
        checkState = Qt.CheckState(index.data(Qt.ItemDataRole.CheckStateRole))
        
        # Xác định theme (Dark hoặc Light)
        theme = Theme.DARK if isDarkTheme() else Theme.LIGHT
        # Kích thước của hình chữ nhật (rect) để vẽ SVG
        icon_size = 15  # Kích thước của icon (25x25)
        # Tính tâm của option.rect
        center = option.rect.center()
        # Tính vị trí góc trên bên trái của rect sao cho tâm của rect trùng với tâm của option.rect
        x = center.x() - icon_size / 2
        y = center.y() - icon_size / 2
        # Tạo QRectF với tâm trùng với tâm của option.rect
        rect = QRectF(x, y, icon_size, icon_size)
        # favotite_rect = QRectF(option.rect.x(), option.rect.y(), 25, 45)
        self.on_favorite_btn = False
        mouse_pos = self.mouse_pos
        if checkState == Qt.CheckState.Checked:
            FI.FAVORITE.render(painter, rect, Theme.DARK)
        else:
            if index.row()==self.hoverRow:
                FI.HEART.render(painter, rect, Theme.DARK)
                if isinstance(mouse_pos,QPoint):
                    if rect.contains(mouse_pos):
                        self.on_favorite_btn = True
                        FI.FAVORITE.render(painter, rect, Theme)
        
    def _drawTokenIcon(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
         # Lấy trạng thái check (nếu cần)
        checkState = Qt.CheckState(index.data(Qt.ItemDataRole.CheckStateRole))

        # Xác định theme (Dark hoặc Light)
        theme = Theme.DARK if isDarkTheme() else Theme.LIGHT

        # Kích thước của hình chữ nhật (rect) để vẽ SVG
        icon_size = 25  # Kích thước của icon (25x25)

        # Tính tâm của option.rect
        center = option.rect.center()

        # Tính vị trí góc trên bên trái của rect sao cho tâm của rect trùng với tâm của option.rect
        x = center.x() - icon_size / 2
        y = center.y() - icon_size / 2

        # Tạo QRectF với tâm trùng với tâm của option.rect
        rect = QRectF(x, y, icon_size, icon_size)

        # Vẽ icon SVG bằng painter
        # symbol_icon = get_symbol_icon(symbol) #symbol = "BTC/USDT"
        # symbol_icon = "btc"
        symbol_icon = self.data[index.row()][6]
        CI.render(painter,rect, symbol_icon)
        
 
    def _drawExchangeIcon(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
         # Lấy trạng thái check (nếu cần)
        checkState = Qt.CheckState(index.data(Qt.ItemDataRole.CheckStateRole))

        # Xác định theme (Dark hoặc Light)
        theme = Theme.DARK if isDarkTheme() else Theme.LIGHT

        # Kích thước của hình chữ nhật (rect) để vẽ SVG
        icon_size = 25  # Kích thước của icon (25x25)

        # Tính tâm của option.rect
        center = option.rect.center()

        # Tính vị trí góc trên bên trái của rect sao cho tâm của rect trùng với tâm của option.rect
        x = center.x() - icon_size / 2
        y = center.y() - icon_size / 2

        # Tạo QRectF với tâm trùng với tâm của option.rect
        rect = QRectF(x, y, icon_size, icon_size)
        
        exchange_icon = self.data[index.row()][5]

        EI.render(painter, rect, exchange_icon)
        

class PositionModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data
        self._check_states:dict = {}

    def rowCount(self, index):
        "giới hạn số lượng hàng"
        return len(self._data)

    def columnCount(self, index):
        return 5

    def data(self, index: QModelIndex, role):
        "để thêm các vai trò cho cell, column, row theo dựa vào index, quy định nội dung và cách thức hiện thị cho bảng"
        if role == Qt.CheckStateRole:
            state = self._data[index.row()][7] 
            return Qt.CheckState.Checked if (state == Qt.CheckState.Checked) else Qt.CheckState.Unchecked
            
        elif role == Qt.DisplayRole:
            if index.column() == 2:
                return self._data[index.row()][2]
            elif index.column() == 3:
                return self._data[index.row()][3]
            # return self._data[index.row()][index.column()]
        elif role == Qt.TextAlignmentRole:
            "Thiết lập căn chỉnh lề cho từng cột"
            if index.column() == 2:
                return Qt.AlignVCenter|Qt.AlignLeft
            if index.column() == 3:
                return Qt.AlignVCenter|Qt.AlignRight
        
    def update_row(self,row,column, value):
        index = self.index(row, column)
        self.setData(index, value, Qt.EditRole)
    
    def updateRows(self, rows_to_update):
        """Cập nhật dữ liệu của các hàng cụ thể."""
        for row in rows_to_update:
            if 0 <= row < self.rowCount(None):  # Kiểm tra nếu hàng nằm trong phạm vi hợp lệ
                # Cập nhật dữ liệu cho từng cột trong hàng
                for column in range(self.columnCount(None)):
                    new_value = random.randint(0, 100)  # Giá trị mới ngẫu nhiên
                    index = self.index(row, column)
                    self.setData(index, new_value, Qt.EditRole)
    
    def setData(self, index, value, role):
        # if index.column() == 1:
        #     print("column side pos long/short")
        # elif index.column() == 2:
        #     print("column type pos buy/sell")
        # elif index.column() == 3:
        #     print("column entry time pos")
        # elif index.column() == 4:
        #     print("column close time pos")
        # elif index.column() == 5:
        #     print("column entry price")
        # elif index.column() == 6:
        #     print("column close price")
        # elif index.column() == 6:
        #     print("column quanty pos")
        # elif index.column() == 6:
        #     print("column lavarate price")
        # elif index.column() == 6:
        #     print("column PnL pos")
        # elif index.column() == 6:
        #     print("column MaxDrawdown pos")
        # elif index.column() == 6:
        #     print("column Fee pos")
        # elif index.column() == 6:
        #     print("column Balance")
        if role == Qt.CheckStateRole:
            # Lưu trạng thái checkbox mới
            if index.column() == 0:
                self.dataChanged.emit(index, index,Qt.CheckStateRole)  # Thông báo thay đổi
                return True
        elif role == Qt.EditRole:
            # self._data[index.row()][index.column()] = value
            self.dataChanged.emit(index, index,Qt.EditRole)
            return True
        return False

    def flags(self, index):
        # Cho phép cell có thể được check/uncheck
        return Qt.ItemIsEnabled | super().flags(index) | Qt.ItemIsUserCheckable


class PositionTable(TableView):
    def __init__(self, parent=None,exchange_id="binance",sig_change_symbol=None):
        super().__init__(parent)
        
        self.verticalHeader().hide()
        self.setBorderRadius(8)
        self.setBorderVisible(True)
        
        self.verticalHeader().setDefaultSectionSize(45)
        
        
        hor_header = self.horizontalHeader()
        ver_header = self.verticalHeader()

        self.exchange_id = exchange_id
        self.sig_change_symbol = sig_change_symbol
        
        dict_data, dict_favorites = self.get_symbols(self.exchange_id)
        
        echange_icon_path,exchange_name,_mode = get_exchange_icon(self.exchange_id)
        
        self.data = {}
        for index,symbol in enumerate(dict_data):
            symbol_icon = get_symbol_icon(symbol)
            if symbol in dict_favorites:
                state = Qt.CheckState.Checked
            else:
                state = Qt.CheckState.Unchecked
            self.data[index] = ['', '', symbol, exchange_name, '',self.exchange_id,symbol_icon, state,echange_icon_path,_mode]
        
        print(len(self.data))
        self.delegate = PositionItemDelegate(self)
        self.setItemDelegate(self.delegate)
        
        # self.resizeColumnsToContents()
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSortingEnabled(True)
        
        
        self.pos_model = PositionModel(self.data)

        self.setModel(self.pos_model)
        
        # Đặt chế độ resize cho cột đầu tiên (cột 0)
        hor_header.setSectionResizeMode(0, QHeaderView.Fixed)  # Cố định kích thước
        ver_header.setSectionResizeMode(0, QHeaderView.Fixed)  # Cố định kích thước
        hor_header.resizeSection(0, 45)  # Đặt chiều rộng là 100 pixel
        ver_header.resizeSection(0, 45)  # Đặt chiều rộng là 100 pixel

        hor_header.setSectionResizeMode(1, QHeaderView.Fixed)  # Cố định kích thước
        ver_header.setSectionResizeMode(1, QHeaderView.Fixed)  # Cố định kích thước
        hor_header.resizeSection(1, 45)  # Đặt chiều rộng là 100 pixel
        ver_header.resizeSection(1, 45)  # Đặt chiều rộng là 100 pixel

        hor_header.setSectionResizeMode(4, QHeaderView.Fixed)  # Cố định kích thước
        ver_header.setSectionResizeMode(4, QHeaderView.Fixed)  # Cố định kích thước
        hor_header.resizeSection(4, 45)  # Đặt chiều rộng là 100 pixel
        ver_header.resizeSection(4, 45)  # Đặt chiều rộng là 100 pixel
        
        hor_header.setSectionResizeMode(2, QHeaderView.Stretch)  # Hoặc QHeaderView.ResizeToContents
        hor_header.setSectionResizeMode(3, QHeaderView.Stretch)  # Hoặc QHeaderView.ResizeToContents
        
        max_rows = 10  # Giới hạn số hàng hiển thị
        row_height = self.rowHeight(0)
        self.setFixedHeight(max_rows * row_height + self.horizontalHeader().height())
        # self.pos_model.dataChanged.connect(self.item_changed)
        self.clicked.connect(self.item_changed)
        
    def get_symbols(self,exchange_id="binance"):
        dict_data = AppConfig.get_config_value(f"topbar.symbol.{exchange_id}")
        dict_favorites = AppConfig.get_config_value(f"topbar.symbol.favorite.{exchange_id}")
        print(dict_favorites)
        print(dict_data)
        return dict_data, dict_favorites
    
    def item_changed(self, index):
        "click on cell, item là PySide6.QtCore.QModelIndex(19,3,0x0,PositionModel(0x1d787459870)) tại cell đó"
        if index.column() == 0:
            checkState = Qt.CheckState(index.data(Qt.ItemDataRole.CheckStateRole))
            if checkState==Qt.CheckState.Checked:
                new_state = self.data[index.row()][7] = Qt.CheckState.Unchecked
            else:
                new_state = self.data[index.row()][7] = Qt.CheckState.Checked
            self.pos_model.setData(index,new_state,Qt.CheckStateRole)
            self.update(index)
            return
        
        # self.data[index] = ['', '', symbol, exchange_name, '',self.exchange_id,symbol_icon, state,echange_icon_path,_mode]
        # ("change_symbol",symbol,self.exchange_id,exchange_name,symbol_icon_path,echange_icon_path,_mode)
        self.symbol_infor = ("change_symbol",self.data[index.row()][2],self.exchange_id,self.data[index.row()][3],self.data[index.row()][6],self.data[index.row()][8],self.data[index.row()][9])
        print(self.data[index.row()])
        print(self.symbol_infor)
        # self.sig_change_symbol.emit(self.symbol_infor)
    def leaveEvent(self,ev):
        # print("leaveEvent")
        super().leaveEvent(ev)
    
    def enterEvent(self,ev):
        # print("enterEvent")
        super().leaveEvent(ev)
    
    def mouseMoveEvent(self,ev:QMouseEvent):
        pos = ev.pos()
        index = self.indexAt(pos)
        self.row_hover = index.row()
        self.delegate.setHoverRow(index.row())
        self.delegate.mouse_pos = pos        
        self.pos_model.dataChanged.emit(index, index)
        super().mouseMoveEvent(ev)

    def mousePressEvent(self,ev:QMouseEvent):
        super().mousePressEvent(ev)
            
    
class RealTimeTable(QWidget):
    def __init__(self,exchange_id="binance"):
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
        
        
        self.table_view = PositionTable(self,exchange_id)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

        # self.timer = QTimer()
        # self.timer.timeout.connect(self.update_table)
        # self.timer.start(1000)  # Cập nhật mỗi 1 giây

    def update_table(self):
        """Cập nhật dữ liệu của các hàng cụ thể trong bảng."""
        # Ví dụ chỉ cập nhật các hàng 2, 4 và 6
        rows_to_update = [2, 4, 6]
        self.table_view.model().updateRows(rows_to_update)


import os
import sys
# -----------------------------------------------------------------------------
import asyncio
import winloop
if hasattr(asyncio, 'WindowsSelectorEventLoopPolicy'):
    try:
        # asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        winloop.install()
    except:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
# -----------------------------------------------------------------------------

import ccxt  # noqa: E402
# -----------------------------------------------------------------------------
binance = ccxt.binanceusdm({
    'apiKey': '',
    'secret': '',
})
symbol = 'BTC/USDT'
timeframe = '1m'

# each ohlcv candle is a list of [ timestamp, open, high, low, close, volume ]
index = 4  # use close price from each ohlcv candle

height = 15
length = 80
import polars as pl
import pandas as pd
from atklip.controls.pandas_ta.overlap.ema import ema as pandas_ema


import time

# Bắt đầu đo thời gian
def print_chart(exchange, symbol, timeframe):
    # get a list of ohlcv candles
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe,limit=1500)
    
    df_pandas = pd.DataFrame(ohlcv,columns=["datetime", "open", "high", "low", "close", "volume"]
        )

    # Lấy cột close
    pandas_close_column = df_pandas["close"]
            

    pandas_ema_data = pandas_ema(pandas_close_column, 200,talib=True)
    
    return df_pandas
    

    

if __name__ == "__main__":
    setTheme(Theme.DARK,True,True)
    app = QApplication(sys.argv)
    
    window = RealTimeTable()
    window.resize(600, 400)
    window.show()
    sys.exit(app.exec())

