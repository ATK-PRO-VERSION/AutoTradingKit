# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'checkbox_value.ui'
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

from atklip.gui.qfluentwidgets  import (CardWidget, CheckBox, TitleLabel)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(385, 35)
        Form.setMinimumSize(QSize(0, 35))
        Form.setMaximumSize(QSize(16777215, 35))
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 1, 5, 1)
        self.tittle = TitleLabel(Form)
        self.tittle.setObjectName(u"tittle")
        self.tittle.setMinimumSize(QSize(0, 33))
        self.tittle.setMaximumSize(QSize(16777215, 33))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.tittle.setFont(font)

        self.horizontalLayout.addWidget(self.tittle)

        self.value = CheckBox(Form)
        self.value.setObjectName(u"value")
        self.value.setMinimumSize(QSize(33, 33))
        self.value.setMaximumSize(QSize(33, 33))

        self.horizontalLayout.addWidget(self.value)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.tittle.setText(QCoreApplication.translate("Form", u"Checkbox", None))
        self.value.setText("")
    # retranslateUi

