
from atklip.gui.qfluentwidgets.components import DateEdit,TimeEdit
from atklip.gui.qfluentwidgets.components.container import HWIDGET,HBoxLayout
from atklip.gui.qfluentwidgets.common import FluentStyleSheet
from atklip.gui.qfluentwidgets import FluentIcon as FIF
from atklip.gui.components import TextButton,MovingWidget

from PySide6.QtWidgets import QWidget, QFrame
from PySide6.QtCore import Qt,QDate
import datetime

from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from views.mainlayout import MainWidget

from atklip.gui.qfluentwidgets.components.date_time.fast_calendar_view import FastCalendarView


class CalendarView(FastCalendarView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(316,360)
        # self.dayView.setFixedHeight(360)
        # self.monthView.setFixedHeight(360)
        # self.yearView.setFixedHeight(360)
    def setDate(self, date: QDate):
        """ set the selected date """
        self.dayView.setDate(date)
        self.date = date
        self.dayView.update()
        self.update()
    def _onDayItemClicked(self, date: QDate):
        # self.close()
        if date != self.date:
            self.date = date
            self.dateChanged.emit(date)
            
    

class GotoButton(HWIDGET):
    def __init__(self,parent:QWidget=None):
        super(GotoButton, self).__init__(parent)
        self._parent = parent
        self.btn_goto = TextButton("Goto",self,None)
        self.btn_goto.setFixedSize(100,35)
        self.btn_cancel = TextButton("Cancel",self,None)
        self.btn_cancel.setFixedSize(100,35)
        self.addSpacer()
        self.addWidget(self.btn_cancel)
        self.addWidget(self.btn_goto)
        self.setSpacing(5)
        self.setContentsMargins(8,1,8,5)
        



class DatePicker(DateEdit):
    def __init__(self,parent:QWidget=None):
        super(DatePicker, self).__init__(parent)

class TimePicker(TimeEdit):
    def __init__(self,parent:QWidget=None):
        super(TimePicker,self).__init__(parent)

class DateTimeMenu(MovingWidget):
    def __init__(self,sig_remove_menu,parent:QWidget=None):
        super(DateTimeMenu, self).__init__(parent,"Goto")
        self._parent:MainWidget = parent
        self.title.btn_close.clicked.connect(sig_remove_menu,Qt.ConnectionType.AutoConnection)
        self.setContentsMargins(0,0,0,10)
        # self.setSpacing(5)
        self.setFixedWidth(320)
        #self.addSeparator(_type = "HORIZONTAL",w=self.width(),h=2)

        self.datetime_widget = QWidget(self)
        self.date_time_layout = HBoxLayout(self.datetime_widget)
        # self.date_time_layout.setContentsMargins(2,2,2,2)
        self.date_time_layout.setSpacing(2)

        self._DatePicker = DatePicker(self)
        self._DatePicker.setFixedWidth(155)
        self._DatePicker.setFixedHeight(35)
        self._DatePicker.dateChanged.connect(self.change_date)
        self.date_time_layout.addWidget(self._DatePicker)
        
        self._TimePicker = TimePicker(self)
        self._TimePicker.setFixedWidth(155)
        self._TimePicker.setFixedHeight(35)
        self.date_time_layout.addWidget(self._TimePicker)

        self.addWidget(self.datetime_widget,0,alignment=Qt.AlignmentFlag.AlignHCenter)
        #self.addSeparator(_type = "HORIZONTAL",w=self.width(),h=2)
        
        self._CalendarPicker = CalendarView(self)
        self.addWidget(self._CalendarPicker,0,alignment=Qt.AlignmentFlag.AlignHCenter)
        self._CalendarPicker.dateChanged.connect(self.change_date)
        
        w = self._CalendarPicker.width()
        # self.addSeparator(_type = "HORIZONTAL",w=w,h=2)
        self.btn_widget = QWidget(self)
        self.btn_widget_layout = HBoxLayout(self.btn_widget)
        self.btn_widget_layout.setContentsMargins(0,10,0,0)
        self.btn_goto_close = GotoButton(self)
        self.btn_widget_layout.addWidget(self.btn_goto_close,0,alignment=Qt.AlignmentFlag.AlignHCenter)
        self.addWidget(self.btn_widget)
        
        self.btn_goto_close.btn_goto.clicked.connect(self.gotodate)
        self.btn_goto_close.btn_cancel.clicked.connect(self.hide)
        
        self._DatePicker.setDate(self._CalendarPicker.date)
        
        _height = self.height()
        
        _height += self.title.height()
        _height +=  self._DatePicker.height()
        _height +=  self._CalendarPicker.height()
        _height += self.btn_goto_close.height()
        
        self.setFixedSize(w,_height+2)

        FluentStyleSheet.DATETIMEMENU.apply(self)
    
    def change_date(self):
        obj = self.sender()
        if isinstance(obj,DatePicker):
            self._CalendarPicker.setDate(obj.date())
        else:
            self._DatePicker.setDate(obj.date)
        _time = self.get_time()
        
    def gotodate(self):
        self.hide()
        _time = self.get_time()
        print(_time)
        self._parent.chartbox_splitter.chart.on_replay_reset_worker(_time,True)
    def get_time(self):
        date_picker = self._DatePicker.date()
        _time = self._TimePicker.time()
        year = date_picker.year()
        day = date_picker.day()
        month = date_picker.month()
        hour = _time.hour()
        sec = _time.second()
        minute = _time.minute()
        date_string = f"{year}-{month}-{day} {hour}:{minute}:{sec}"
        dt_object = datetime.datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        timestamp = int(dt_object.timestamp())
        return timestamp
    
        