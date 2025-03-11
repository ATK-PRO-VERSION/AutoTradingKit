# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'edit_value.ui'
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

from atklip.gui.qfluentwidgets  import (CardWidget, LineEdit, TitleLabel)

class Ui_text_value(object):
    def setupUi(self, text_value):
        if not text_value.objectName():
            text_value.setObjectName(u"text_value")
        text_value.resize(320, 35)
        text_value.setMinimumSize(QSize(0, 35))
        text_value.setMaximumSize(QSize(16777215, 35))
        self.horizontalLayout = QHBoxLayout(text_value)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 1, 5, 1)
        self.tittle = TitleLabel(text_value)
        self.tittle.setObjectName(u"tittle")
        self.tittle.setMinimumSize(QSize(0, 33))
        self.tittle.setMaximumSize(QSize(16777215, 33))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.tittle.setFont(font)

        self.horizontalLayout.addWidget(self.tittle)

        self.value = LineEdit(text_value)
        self.value.setObjectName(u"value")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.value.sizePolicy().hasHeightForWidth())
        self.value.setSizePolicy(sizePolicy)

        self.horizontalLayout.addWidget(self.value)


        self.retranslateUi(text_value)

        QMetaObject.connectSlotsByName(text_value)
    # setupUi

    def retranslateUi(self, text_value):
        text_value.setWindowTitle(QCoreApplication.translate("text_value", u"Form", None))
        self.tittle.setText(QCoreApplication.translate("text_value", u"Title label", None))
    # retranslateUi

