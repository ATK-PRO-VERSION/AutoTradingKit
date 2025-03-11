# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'iconwidget_with_text_button.ui'
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

from atklip.gui.qfluentwidgets import (CardWidget, IconWidget, TitleLabel)
from atklip.gui.qfluentwidgets import resource as resource_rc

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(301, 40)
        Form.setMinimumSize(QSize(200, 40))
        Form.setMaximumSize(QSize(16777215, 45))
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(5, 1, 5, 1)
        self.exchange_icon = IconWidget(Form)
        self.exchange_icon.setObjectName(u"exchange_icon")
        self.exchange_icon.setMinimumSize(QSize(25, 25))
        self.exchange_icon.setMaximumSize(QSize(25, 25))

        self.horizontalLayout.addWidget(self.exchange_icon)

        self.TitleLabel = TitleLabel(Form)
        self.TitleLabel.setObjectName(u"TitleLabel")
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.TitleLabel.setFont(font)

        self.horizontalLayout.addWidget(self.TitleLabel)


        self.retranslateUi(Form)

        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.TitleLabel.setText(QCoreApplication.translate("Form", u"Title label", None))
    # retranslateUi

