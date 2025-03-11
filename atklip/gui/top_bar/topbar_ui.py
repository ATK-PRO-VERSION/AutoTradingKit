# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'topbar.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLayout,
    QSizePolicy, QSpacerItem, QWidget)

class Ui_Frame(object):
    def setupUi(self, Frame):
        if not Frame.objectName():
            Frame.setObjectName(u"Frame")
        Frame.resize(616, 45)
        Frame.setMinimumSize(QSize(0, 45))
        Frame.setMaximumSize(QSize(16777215, 45))
        self.horizontalLayout = QHBoxLayout(Frame)
        self.horizontalLayout.setSpacing(5)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setSizeConstraint(QLayout.SetMaximumSize)
        self.horizontalLayout.setContentsMargins(5, 1, 10, 1)
        self.left_layout = QHBoxLayout()
        self.left_layout.setSpacing(5)
        self.left_layout.setObjectName(u"left_layout")
        self.left_layout.setSizeConstraint(QLayout.SetMaximumSize)
        self.left_layout.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout.addLayout(self.left_layout)

        self.horizontalSpacer = QSpacerItem(1000000000, 1, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.right_layout = QHBoxLayout()
        self.right_layout.setSpacing(5)
        self.right_layout.setObjectName(u"right_layout")
        self.right_layout.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout.addLayout(self.right_layout)


        self.retranslateUi(Frame)

        QMetaObject.connectSlotsByName(Frame)
    # setupUi

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QCoreApplication.translate("Frame", u"Frame", None))
    # retranslateUi

