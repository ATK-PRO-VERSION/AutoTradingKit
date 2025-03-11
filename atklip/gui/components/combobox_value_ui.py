# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'combobox_value.ui'
##
## Created by: Qt User Interface Compiler version 6.8.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QSizePolicy, QWidget)

from atklip.gui.qfluentwidgets  import (CardWidget, ComboBox, TitleLabel)

class Ui_combobox_value(object):
    def setupUi(self, combobox_value):
        if not combobox_value.objectName():
            combobox_value.setObjectName(u"combobox_value")
        combobox_value.resize(345, 35)
        combobox_value.setMinimumSize(QSize(0, 35))
        combobox_value.setMaximumSize(QSize(16777215, 35))
        self.horizontalLayout = QHBoxLayout(combobox_value)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 1, 5, 1)
        self.tittle = TitleLabel(combobox_value)
        self.tittle.setObjectName(u"tittle")
        self.tittle.setMinimumSize(QSize(0, 33))
        self.tittle.setMaximumSize(QSize(16777215, 33))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.tittle.setFont(font)

        self.horizontalLayout.addWidget(self.tittle)

        self.value = ComboBox(combobox_value)
        self.value.setObjectName(u"value")
        self.value.setMinimumSize(QSize(0, 33))
        self.value.setMaximumSize(QSize(16777215, 33))

        self.horizontalLayout.addWidget(self.value)


        self.retranslateUi(combobox_value)

        QMetaObject.connectSlotsByName(combobox_value)
    # setupUi

    def retranslateUi(self, combobox_value):
        combobox_value.setWindowTitle(QCoreApplication.translate("combobox_value", u"Form", None))
        self.tittle.setText(QCoreApplication.translate("combobox_value", u"Title label", None))
    # retranslateUi

