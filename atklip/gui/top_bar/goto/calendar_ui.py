# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'calendar.ui'
##
## Created by: Qt User Interface Compiler version 6.7.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize)
from PySide6.QtWidgets import (QCalendarWidget, QSizePolicy,
    QVBoxLayout)

class Ui_Frame(object):
    def setupUi(self, Frame):
        if not Frame.objectName():
            Frame.setObjectName(u"Frame")
        Frame.resize(320, 300)
        Frame.setMaximumSize(QSize(320, 300))
        Frame.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(Frame)
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(1, 1, 1, 1)
        self.calendarview = QCalendarWidget(Frame)
        self.calendarview.setObjectName(u"calendarview")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.calendarview.sizePolicy().hasHeightForWidth())
        self.calendarview.setSizePolicy(sizePolicy)
        self.calendarview.setMinimumSize(QSize(0, 300))
        self.calendarview.setMaximumSize(QSize(320, 300))
        self.calendarview.setStyleSheet(u"")
        self.calendarview.setGridVisible(True)
        self.calendarview.setSelectionMode(QCalendarWidget.SingleSelection)
        self.calendarview.setHorizontalHeaderFormat(QCalendarWidget.NoHorizontalHeader)
        self.calendarview.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        self.calendarview.setNavigationBarVisible(True)
        self.calendarview.setDateEditEnabled(True)

        self.verticalLayout.addWidget(self.calendarview)


        self.retranslateUi(Frame)

        QMetaObject.connectSlotsByName(Frame)
    # setupUi

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QCoreApplication.translate("Frame", u"Frame", None))
    # retranslateUi

