from PySide6.QtCore import QAbstractTableModel, Qt, QCoreApplication, QModelIndex
from PySide6.QtGui import QColor
from PySide6.QtCore import Signal,Qt
# from asyncqt import QtCore


class DataGridModel(QAbstractTableModel):
  # https://stackoverflow.com/questions/64287713/how-can-you-set-header-labels-for-qtableview-columns
  set_data = Signal(tuple)
  def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...):
    if orientation == Qt.Horizontal and role == Qt.DisplayRole:
      # return f"Column {section + 1}"
      return self._headerNames[section]
    if orientation == Qt.Vertical and role == Qt.DisplayRole:
      return f"{section + 1}"

  def __init__(self, 
               parent=None, 
               columns=None,
               rows=None,
               ):
    # self.setRowCount(0)
    self._headerNames = [item.get('headerName') if item.get('headerName') else ""  for item in columns]
    
    super(DataGridModel, self).__init__(parent)

    self._parent = parent
    self._columns = columns
    self._rows = rows
    self.colors = dict()
    self.set_data.connect(self._parent.setIndexWidget,Qt.ConnectionType.AutoConnection)

  def restranUi(self):
    pass
    # QCoreApplication.translate("MainWindow", u"Form", None)

  def rowCount(self, n=None):
    return len(self._rows)

  def columnCount(self, n=None):
    return len(self._columns)

  def flags(self, index: QModelIndex) -> Qt.ItemFlags:
    return Qt.ItemIsDropEnabled | Qt.ItemIsEnabled | Qt.ItemIsEditable | Qt.ItemIsSelectable | Qt.ItemIsDragEnabled

  def supportedDropActions(self) -> bool:
    return Qt.MoveAction | Qt.CopyAction

  def data(self, index, role=Qt.ForegroundRole):
    if index.isValid():
      if role == Qt.ItemDataRole.DisplayRole or role == Qt.EditRole:
        try:
          # print('aaaaaaaaaaaa___________', self._rows[index.row()][self._columns[index.column()].get("field")])
          # print('aaaaaaaaaaaa___________', self._rows[index.row()][index.column()])
          renderCell = self._columns[index.column()].get("renderCell")
          if renderCell:
            options = self._rows[index.row()]
            cell = renderCell(options)
            if not self.parent().indexWidget(index):
              self.set_data.emit(index, cell)
            return ""
          else:
            value = str(self._rows[index.row()][self._columns[index.column()].get("field")])

        except Exception as e:
          print(str(e))
          value = None
        return value or ""

      if role == Qt.BackgroundRole:
        # color = self.colors.get((index.row(), index.column()))
        color = None
        if color is not None:
          return color

      if role == Qt.ForegroundRole:
        try:
          # value = str(self._rows[index.row()][index.column()])
          value = ''
        except IndexError:
          value = ""

      # if role == Qt.TextAlignmentRole:
      #   if self._columns[index.column()].get("align") == "left":
      #     return int(Qt.AlignLeft | Qt.AlignVCenter)
      #   elif self._columns[index.column()].get("align") == "center":
      #     return int(Qt.AlignCenter | Qt.AlignVCenter)
      #   if self._columns[index.column()].get("align") == "right":
      #     return int(Qt.AlignRight | Qt.AlignVCenter)

  def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
    try:
      curentValue = self._rows[index.row()][self._columns[index.column()].get("field")]
    except IndexError:
      curentValue = ' '
    if not index.isValid():
      return False

    if role == Qt.ItemDataRole.EditRole:
      #print(377, 'setData tableView')
      if value == "":
        return False
      if value != curentValue and value != "":
        try:
          self._rows[index.row()][self._columns[index.column()].get("field")]= value
        except:
          return False
      else:
        self._rows[index.row()][self._columns[index.column()].get("field")] = curentValue
      return True

    return False

  # @QtCore.Slot(int, int, QtCore.QVariant)
  def update_item(self, row, col, value):
    ix = self.index(row, col)
    self.setData(ix, value)
    
  def change_color(self, row, column, color):
    ix = self.index(row, column)
    self.colors[(row, column)] = color
    self.dataChanged.emit(ix, ix, (Qt.BackgroundRole,))
