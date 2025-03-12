# coding: utf-8
import random
import re
import traceback
from typing import List

from PySide6.QtCore import Qt, QMargins, QModelIndex, QRectF,Qt, \
    QAbstractTableModel, QModelIndex,QPointF,QPoint,Signal
from PySide6.QtGui import QPainter, QColor, QPalette, QBrush, QMouseEvent
from PySide6.QtWidgets import (QStyledItemDelegate, QApplication, QStyleOptionViewItem,QHeaderView,
                             QTableView, QWidget)

from atklip.appmanager.setting.config import AppConfig
from atklip.exchanges.crypto import CryptoExchange
from atklip.gui.qfluentwidgets.common.icon import check_icon_exist, get_exchange_icon
from atklip.gui.qfluentwidgets.components import isDarkTheme, Theme, TableView,getFont
from atklip.gui.qfluentwidgets.common import FluentIcon as FI,CryptoIcon as CI, EchangeIcon as EI
from atklip.gui.qfluentwidgets.components.widgets.label import TitleLabel

from atklip.gui.qfluentwidgets.common import get_symbol_icon

class PositionItemDelegate(QStyledItemDelegate):
    def __init__(self, parent: QTableView):
        super().__init__(parent)
        self._parent = parent
        self.margin = 2
        self.hoverRow = -1
        self.pressedRow = -1
        self.mouse_pos:QPointF|QPoint = None
        self.selectedRows = set()
        self.on_favorite_btn = False
        # self._data = self._parent.table_model._data
    
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
        if self._parent.table_model._data:
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
            
            if index.column() == 1:
                self._drawTokenIcon(painter, option, index)
            elif index.column() == 4:
                    self._drawExchangeIcon(painter, option, index)
            elif index.column() == 0:
                self._drawFavorite(painter, option, index)
            
            painter.restore()
            super().paint(painter, option, index)
        else:
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
        # checkState = Qt.CheckState(index.data(Qt.ItemDataRole.CheckStateRole))

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
        symbol_icon = self._parent.table_model._data[index.row()][6]
        CI.render(painter,rect, symbol_icon)
        
 
    def _drawExchangeIcon(self, painter: QPainter, option: QStyleOptionViewItem, index: QModelIndex):
         # Lấy trạng thái check (nếu cần)
        # checkState = Qt.CheckState(index.data(Qt.ItemDataRole.CheckStateRole))

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
        
        exchange_icon = self._parent.table_model._data[index.row()][8]

        EI.render(painter, rect, exchange_icon)
        

class PositionModel(QAbstractTableModel):
    def __init__(self, data):
        super().__init__()
        self._data = data if data is not None else []
        self._original_data = self._data.copy()
        self._check_states:dict = {}

    @property
    def _original_data(self):
        return self.original_data
    @_original_data.setter
    def _original_data(self,_original_data):
        self.original_data=_original_data

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return 5
    
    def removeRow(self, row, parent=QModelIndex()):
        if row < 0 or row >= self.rowCount():
            return False
        # Thông báo cho view biết hàng sắp bị xóa
        self.beginRemoveRows(parent, row, row)
        del self._data[row]  # Xóa hàng khỏi dữ liệu nội bộ
        self._original_data = self._data.copy()
        self.endRemoveRows()  # Kết thúc xóa hàng
        return True
    
    def addRow(self, row_data, parent=QModelIndex()):
        # Thêm hàng mới vào cuối danh sách
        row_position = self.rowCount()
        # Thông báo cho view biết hàng mới sắp được thêm
        self.beginInsertRows(parent, row_position, row_position)
        self._data.append(row_data)  # Thêm dữ liệu mới vào danh sách
        self._original_data = self._data.copy()
        self.endInsertRows()  # Kết thúc thêm hàng
        return True
    
    def updateRow(self, row, new_data, parent=QModelIndex()):
        # Kiểm tra xem hàng có hợp lệ không
        if row < 0 or row >= self.rowCount():
            return False
        # Cập nhật dữ liệu của hàng
        self._data[row] = new_data
        self._original_data = self._data.copy()
        # Thông báo cho view biết dữ liệu đã thay đổi
        top_left = self.index(row, 0)
        bottom_right = self.index(row, self.columnCount() - 1)
        self.dataChanged.emit(top_left, bottom_right)
        return True
    
    def insertRow(self, row, row_data, parent=QModelIndex()):
        # Kiểm tra xem vị trí chèn có hợp lệ không
        if row < 0 or row > self.rowCount():
            return False
        # Thông báo cho view biết hàng mới sắp được chèn
        self.beginInsertRows(parent, row, row)
        self._data.insert(row, row_data)  # Chèn dữ liệu mới vào danh sách
        self._original_data = self._data.copy()
        self.endInsertRows()  # Kết thúc chèn hàng
        return True
    
    def resetData(self, new_data):
        # Xóa toàn bộ dữ liệu cũ và thay thế bằng dữ liệu mới
        self.beginResetModel()  # Thông báo cho view biết dữ liệu sắp thay đổi
        self._data = new_data
        self._original_data = self._data.copy()
        self.endResetModel()  # Kết thúc thay đổi dữ liệu
    
    def filterData(self, keyword:str=""):
        # Lọc dữ liệu dựa trên từ khóa (cột Name)
        filtered_data = [
            row for row in self._original_data
            if str(row[2].lower()).startswith(keyword.lower())   # Lọc theo cột Name (index 1)
        ]
        self.beginResetModel()
        self._data = filtered_data
        self.endResetModel()
    
    def data(self, index: QModelIndex, role):
        "để thêm các vai trò cho cell, column, row theo dựa vào index, quy định nội dung và cách thức hiện thị cho bảng"
        if self._data:
            if role == Qt.ItemDataRole.CheckStateRole:
                state = self._data[index.row()][7] 
                return Qt.CheckState.Checked if (state == Qt.CheckState.Checked) else Qt.CheckState.Unchecked
                
            elif role == Qt.ItemDataRole.DisplayRole:
                if index.column() == 2:
                    return self._data[index.row()][2]
                elif index.column() == 3:
                    return self._data[index.row()][3]
            elif role == Qt.ItemDataRole.TextAlignmentRole:
                "Thiết lập căn chỉnh lề cho từng cột"
                if index.column() == 2:
                    return Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft
                elif index.column() == 3:
                    return Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignRight

    def flags(self, index):
        # Cho phép cell có thể được check/uncheck
        return Qt.ItemIsEnabled | super().flags(index) | Qt.ItemIsUserCheckable
    
class BaseMenu(TableView):
    # sig_show_process = Signal(bool)
    # sig_update_symbol = Signal(int)
    # sig_add_item = Signal(object)
    # sig_remove_item = Signal(object)
    # sig_add_to_favorite = Signal(tuple)
    # sig_update_symbols = Signal(str)
    def __init__(self,sig_add_remove_favorite,sig_change_symbol,parent:QWidget=None,exchange_id:str=""):
        super(BaseMenu,self).__init__(parent)
        self.setObjectName(f"{exchange_id}")
        self.verticalHeader().hide()
        self.horizontalHeader().hide()
        
        self.setBorderRadius(8)
        # self.setBorderVisible(True)
        
        self.verticalHeader().setDefaultSectionSize(45)
        
        self.exchange_id = exchange_id
        self.sig_change_symbol = sig_change_symbol
        self.sig_add_remove_favorite = sig_add_remove_favorite
        
        self._data = []
        self.dict_favorites = {}
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        # self.setSortingEnabled(True)
        
        dict_data, self.dict_favorites = self.get_symbols(self.exchange_id)
        echange_icon_path,exchange_name,_mode = get_exchange_icon(self.exchange_id)
        
        if self.exchange_id != "favorite":
            if dict_data != []:
                for index,symbol in enumerate(dict_data):
                    symbol_icon = get_symbol_icon(symbol)
                    symbol_icon_path = CI.crypto_url(symbol_icon)
                    dict_favorites = self.dict_favorites.get(self.exchange_id,[]) 
                    if dict_favorites !=[]:
                        if symbol in dict_favorites:
                            state = Qt.CheckState.Checked
                        else:
                            state = Qt.CheckState.Unchecked
                    else:
                        state = Qt.CheckState.Unchecked
                    self.data.append(['', '', symbol, exchange_name, '',self.exchange_id,symbol_icon_path, state,echange_icon_path,_mode]) 
        else:
            self.dict_favorites = AppConfig.get_config_value(f"topbar.symbol.favorite")
            if self.dict_favorites == None:
                AppConfig.sig_set_single_data.emit((f"topbar.symbol.favorite",{}))
                self.dict_favorites = {}
            if self.dict_favorites:
                for exchange_id in list(self.dict_favorites.keys()):
                    dict_data = self.dict_favorites.get(exchange_id,[]) 
                    if dict_data != []:
                        echange_icon_path,exchange_name,_mode = get_exchange_icon(exchange_id)
                        for index,symbol in enumerate(dict_data):
                            symbol_icon = get_symbol_icon(symbol)
                            symbol_icon_path = CI.crypto_url(symbol_icon)
                            state = Qt.CheckState.Checked
                            self.data.append(['', '', symbol, exchange_name, '',exchange_id,symbol_icon_path, state,echange_icon_path,_mode])
        
        self.delegate = None
        self.table_model = None
        
        if self._data:
            
            self.table_model = PositionModel(self._data)
            self.setModel(self.table_model)
            
            self.delegate = PositionItemDelegate(self)
            self.setItemDelegate(self.delegate)

            hor_header = self.horizontalHeader()
            ver_header = self.verticalHeader()
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
            
        self.setFixedHeight(600)
        self.clicked.connect(self.item_changed)
    @property
    def _data(self)-> list:
        return self.data 
    
    @_data.setter
    def _data(self, data):
        self.data = data 
    
    def filter_table(self,keyword:str=""):
        self.table_model.filterData(keyword)
    
    def get_symbols(self,exchange_id="binance"):
        dict_data = AppConfig.get_config_value(f"topbar.symbol.{exchange_id}")
        dict_favorites = AppConfig.get_config_value(f"topbar.symbol.favorite")
        if exchange_id != "favorite":
            if not dict_data:
                crypto_ex = CryptoExchange()
                exchange = crypto_ex.setupEchange(exchange_name=exchange_id)
                try:
                    exchange.load_markets()
                    markets = []
                    for market in list(exchange.markets.keys()):
                        if exchange.markets[market]['active'] == True:
                            markets.append(exchange.markets[market]['symbol'])
                    # markets = exchange.symbols
                    if markets != []:
                        symbols = [re.findall(r'(.*?):', market)[0] for market in markets if re.findall(r'(.*?):', market) != []]
                        if symbols == []:
                            symbols = [market for market in markets if re.findall(r'(.*?):', market) == []]

                        for symbol in  symbols:
                            if "/" in symbol:
                                first_symbol = re.findall(r'(.*?)/', symbol)
                                if check_icon_exist(first_symbol[0]):
                                    if symbol not in dict_data:
                                        dict_data.append(symbol)
                                else:
                                    "đây là chỗ tìm coin chưa có icon để bổ sung"
                                    pass
                        "save to config"
                        AppConfig.sig_set_single_data.emit((f"topbar.symbol.{exchange_id}",dict_data))
                        
                except Exception as e:
                    traceback.print_exception(e)
                crypto_ex.deleteLater()
        return dict_data, dict_favorites
    
    def item_changed(self, index):
        "click on cell, item là PySide6.QtCore.QModelIndex(19,3,0x0,PositionModel(0x1d787459870)) tại cell đó"
        self.symbol_infor = ("change_symbol",
                             self.table_model._data[index.row()][2],
                             self.table_model._data[index.row()][5],
                             self.table_model._data[index.row()][3],
                             self.table_model._data[index.row()][6],
                             self.table_model._data[index.row()][8],
                             self.table_model._data[index.row()][9])
        
        if index.column() == 0:
            checkState = Qt.CheckState(index.data(Qt.ItemDataRole.CheckStateRole))
            if checkState==Qt.CheckState.Checked:
                new_state = self.table_model._data[index.row()][7] = Qt.CheckState.Unchecked
            else:
                new_state = self.table_model._data[index.row()][7] = Qt.CheckState.Checked
            new_data = self.table_model._data[index.row()]
            if new_state == Qt.CheckState.Unchecked:
                if self.exchange_id == "favorite":
                    # del self.data[index.row()]
                    self.table_model.removeRow(index.row())
                else:
                    "update data"
                    self.table_model.dataChanged.emit(index, index,Qt.CheckStateRole)
            else:
                if self.exchange_id != "favorite":
                    self.table_model.dataChanged.emit(index, index,Qt.CheckStateRole)
                
            self.sig_add_remove_favorite.emit((self.exchange_id,new_data))
            return
        self.sig_change_symbol.emit(self.symbol_infor)

    def add_remove_favorite_item(self,exchange_id,new_data):
        symbol = new_data[2]
        new_state = new_data[7]
        from_exchange_id = new_data[5]
        if exchange_id == "favorite":
            if self.exchange_id != "favorite":
                for index,row in enumerate(self.data):
                    if row[2] == symbol:
                        self.data[index][7] = new_state
                        self.table_model.updateRow(index, self.data[index])
                        
                        self.dict_favorites = AppConfig.get_config_value(f"topbar.symbol.favorite")
                        if new_state == Qt.CheckState.Unchecked:
                            if self.exchange_id not in list(self.dict_favorites.keys()):
                                self.dict_favorites[self.exchange_id] = []
                            else:
                                if symbol in self.dict_favorites[self.exchange_id]:
                                    self.dict_favorites[self.exchange_id].remove(symbol)
                        else:
                            if self.exchange_id not in list(self.dict_favorites.keys()):
                                self.dict_favorites[self.exchange_id] = [symbol]
                            else:
                                if symbol not in self.dict_favorites[self.exchange_id]:
                                    self.dict_favorites[self.exchange_id].append(symbol)
                        AppConfig.sig_set_single_data.emit((f"topbar.symbol.favorite.{self.exchange_id}",self.dict_favorites[self.exchange_id]))
                        self.dict_favorites = AppConfig.get_config_value(f"topbar.symbol.favorite")
                        break
        else:
            if self.exchange_id == "favorite":
                if new_state == Qt.CheckState.Checked:
                    if self._data == []:
                        self._data = [new_data]
                        if not self.delegate or not self.table_model:
                            
                            self.table_model = PositionModel(self._data)
                            self.setModel(self.table_model)
                            
                            self.delegate = PositionItemDelegate(self)
                            self.setItemDelegate(self.delegate)

                            hor_header = self.horizontalHeader()
                            ver_header = self.verticalHeader()
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
                        else:
                            self.table_model.insertRow(0,new_data)
                    else: 
                        self.table_model.insertRow(0,new_data)
                    if exchange_id != "favorite":
                        self.dict_favorites = AppConfig.get_config_value(f"topbar.symbol.favorite")
                        if new_state == Qt.CheckState.Unchecked:
                            if exchange_id not in list(self.dict_favorites.keys()):
                                self.dict_favorites[exchange_id] = []
                            else:
                                if symbol in self.dict_favorites[exchange_id]:
                                    self.dict_favorites[exchange_id].remove(symbol)
                        else:
                            if exchange_id not in list(self.dict_favorites.keys()):
                                self.dict_favorites[exchange_id] = [symbol]
                            else:
                                if symbol not in self.dict_favorites[exchange_id]:
                                    self.dict_favorites[exchange_id].append(symbol)
                        AppConfig.sig_set_single_data.emit((f"topbar.symbol.favorite.{exchange_id}",self.dict_favorites[exchange_id]))
                        self.dict_favorites = AppConfig.get_config_value(f"topbar.symbol.favorite")    
                    
                else:
                    for index,row in enumerate(self.data):
                        if row[2] == symbol and row[5] == from_exchange_id:
                            self.table_model.removeRow(index)
                            if exchange_id != "favorite":
                                self.dict_favorites = AppConfig.get_config_value(f"topbar.symbol.favorite")
                                if new_state == Qt.CheckState.Unchecked:
                                    if exchange_id not in list(self.dict_favorites.keys()):
                                        self.dict_favorites[exchange_id] = []
                                    else:
                                        if symbol in self.dict_favorites[exchange_id]:
                                            self.dict_favorites[exchange_id].remove(symbol)
                                else:
                                    if exchange_id not in list(self.dict_favorites.keys()):
                                        self.dict_favorites[exchange_id] = [symbol]
                                    else:
                                        if symbol not in self.dict_favorites[exchange_id]:
                                            self.dict_favorites[exchange_id].append(symbol)
                                AppConfig.sig_set_single_data.emit((f"topbar.symbol.favorite.{exchange_id}",self.dict_favorites[exchange_id]))
                                self.dict_favorites = AppConfig.get_config_value(f"topbar.symbol.favorite")  
                            break
                
    def leaveEvent(self,ev):
        super().leaveEvent(ev)
    
    def enterEvent(self,ev):
        super().leaveEvent(ev)
    
    def mouseMoveEvent(self,ev:QMouseEvent):
        pos = ev.position()
        index = self.indexAt(pos.toPoint())
        self.row_hover = index.row()
        if self.delegate:
            self.delegate.setHoverRow(index.row())
            self.delegate.mouse_pos = pos     
        if self.table_model:   
            self.table_model.dataChanged.emit(index, index)
        super().mouseMoveEvent(ev)

    def mousePressEvent(self,ev:QMouseEvent):
        super().mousePressEvent(ev)
            
