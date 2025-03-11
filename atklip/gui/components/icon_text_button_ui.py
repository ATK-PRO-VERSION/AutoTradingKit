# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'icon_text_button.ui'
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


from atklip.gui.components.exchange_icon import ExchangeICon
from atklip.gui.qfluentwidgets import (CardWidget, TitleLabel)
from atklip.gui.qfluentwidgets import resource as resource_rc
class Ui__pushbutton(object):
    def setupUi(self, _pushbutton):
        if not _pushbutton.objectName():
            _pushbutton.setObjectName(u"_pushbutton")
        _pushbutton.resize(250, 40)
        _pushbutton.setMinimumSize(QSize(200, 40))
        _pushbutton.setMaximumSize(QSize(16777215, 45))
        self.horizontalLayout = QHBoxLayout(_pushbutton)
        self.horizontalLayout.setSpacing(10)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 1, -1, 1)
        self.exchange_icon = ExchangeICon(_pushbutton)
        self.exchange_icon.setObjectName(u"exchange_icon")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exchange_icon.sizePolicy().hasHeightForWidth())
        self.exchange_icon.setSizePolicy(sizePolicy)
        self.exchange_icon.setMinimumSize(QSize(30, 30))
        self.exchange_icon.setMaximumSize(QSize(30, 30))
        icon = QIcon()
        icon.addFile(u":/qfluentwidgets/images/exchange/binance_logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.exchange_icon.setIcon(icon)
        self.exchange_icon.setIconSize(QSize(30, 30))
        self.exchange_icon.setAutoDefault(True)
        self.exchange_icon.setFlat(True)

        self.horizontalLayout.addWidget(self.exchange_icon)

        self.TitleLabel = TitleLabel(_pushbutton)
        self.TitleLabel.setObjectName(u"TitleLabel")
        self.TitleLabel.setMinimumSize(QSize(0, 33))
        self.TitleLabel.setMaximumSize(QSize(16777215, 33))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(13)
        font.setBold(False)
        self.TitleLabel.setFont(font)

        self.horizontalLayout.addWidget(self.TitleLabel)


        self.retranslateUi(_pushbutton)

        QMetaObject.connectSlotsByName(_pushbutton)
    # setupUi

    def retranslateUi(self, _pushbutton):
        _pushbutton.setWindowTitle(QCoreApplication.translate("_pushbutton", u"Form", None))
        self.exchange_icon.setText("")
        self.TitleLabel.setText(QCoreApplication.translate("_pushbutton", u"Title label", None))
    # retranslateUi

