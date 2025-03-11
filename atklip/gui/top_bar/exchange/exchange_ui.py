# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'exchange.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QSizePolicy, QVBoxLayout,
    QWidget)

from atklip.gui.components.exchange_icon import ExchangeICon
from atklip.gui.qfluentwidgets import (CardWidget, StrongBodyLabel, SubtitleLabel)

class Ui_cr_exchange(object):
    def setupUi(self, cr_exchange):
        if not cr_exchange.objectName():
            cr_exchange.setObjectName(u"cr_exchange")
        cr_exchange.resize(209, 44)
        cr_exchange.setStyleSheet(u"background-color:transparent;")
        self.horizontalLayout_2 = QHBoxLayout(cr_exchange)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(1, 1, 5, 1)
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.exchange_icon = ExchangeICon(cr_exchange)
        self.exchange_icon.setObjectName(u"exchange_icon")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.exchange_icon.sizePolicy().hasHeightForWidth())
        self.exchange_icon.setSizePolicy(sizePolicy)
        self.exchange_icon.setMinimumSize(QSize(40, 40))
        self.exchange_icon.setMaximumSize(QSize(40, 40))
        icon = QIcon()
        icon.addFile(u":/qfluentwidgets/images/exchange/binance_logo.png", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.exchange_icon.setIcon(icon)
        self.exchange_icon.setIconSize(QSize(40, 40))
        self.exchange_icon.setAutoDefault(True)
        self.exchange_icon.setFlat(True)

        self.horizontalLayout.addWidget(self.exchange_icon)

        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setSpacing(1)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.exchange = StrongBodyLabel(cr_exchange)
        self.exchange.setObjectName(u"exchange")
        self.exchange.setProperty(u"pixelFontSize", 12)

        self.verticalLayout.addWidget(self.exchange)

        self.mode = SubtitleLabel(cr_exchange)
        self.mode.setObjectName(u"mode")
        self.mode.setProperty(u"pixelFontSize", 14)

        self.verticalLayout.addWidget(self.mode)


        self.horizontalLayout.addLayout(self.verticalLayout)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(cr_exchange)

        QMetaObject.connectSlotsByName(cr_exchange)
    # setupUi

    def retranslateUi(self, cr_exchange):
        cr_exchange.setWindowTitle(QCoreApplication.translate("cr_exchange", u"Form", None))
        self.exchange_icon.setText("")
        self.exchange.setText(QCoreApplication.translate("cr_exchange", u"Binance", None))
        self.mode.setText(QCoreApplication.translate("cr_exchange", u"FUTURES", None))
    # retranslateUi

