# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainwidget.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QSizePolicy,
    QSplitter, QVBoxLayout, QWidget)

from atklip.graphics.chart_component.graph_spliter import GraphSplitter
from atklip.gui.draw_bar.draw_bar import DRAW_BAR
from atklip.gui.right_bar.right_bar import RIGHT_BAR
from atklip.gui.top_bar.top_bar import TopBar

class Ui_MainWidget(object):
    def setupUi(self, MainWidget):
        if not MainWidget.objectName():
            MainWidget.setObjectName(u"MainWidget")
        MainWidget.setWindowModality(Qt.NonModal)
        MainWidget.resize(1130, 721)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(MainWidget.sizePolicy().hasHeightForWidth())
        MainWidget.setSizePolicy(sizePolicy)
        font = QFont()
        font.setStyleStrategy(QFont.PreferAntialias)
        MainWidget.setFont(font)
        MainWidget.setStyleSheet(u"")
        self.verticalLayout = QVBoxLayout(MainWidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4 = QVBoxLayout()
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(-1, 0, -1, -1)
        self.frame = QFrame(MainWidget)
        self.frame.setObjectName(u"frame")
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMinimumSize(QSize(0, 47))
        self.frame.setMaximumSize(QSize(16777215, 47))
        self.frame.setFrameShape(QFrame.NoFrame)
        self.frame.setFrameShadow(QFrame.Raised)
        self.verticalLayout_8 = QVBoxLayout(self.frame)
        self.verticalLayout_8.setSpacing(0)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_10 = QVBoxLayout()
        self.verticalLayout_10.setSpacing(0)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.frame_3 = QFrame(self.frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 2))
        self.frame_3.setMaximumSize(QSize(16777215, 2))
        self.frame_3.setStyleSheet(u"background-color: #474747;")
        self.frame_3.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_10.addWidget(self.frame_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.frame_6 = QFrame(self.frame)
        self.frame_6.setObjectName(u"frame_6")
        self.frame_6.setMinimumSize(QSize(2, 0))
        self.frame_6.setMaximumSize(QSize(2, 45))
        self.frame_6.setStyleSheet(u"background-color: #474747;")
        self.frame_6.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout_2.addWidget(self.frame_6)

        self.topbar = TopBar(self.frame)
        self.topbar.setObjectName(u"topbar")
        self.topbar.setMinimumSize(QSize(0, 45))
        self.topbar.setMaximumSize(QSize(16777215, 45))
        self.topbar.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout_2.addWidget(self.topbar)

        self.frame_10 = QFrame(self.frame)
        self.frame_10.setObjectName(u"frame_10")
        self.frame_10.setMinimumSize(QSize(2, 0))
        self.frame_10.setMaximumSize(QSize(2, 45))
        self.frame_10.setLayoutDirection(Qt.LeftToRight)
        self.frame_10.setStyleSheet(u"background-color: #474747;")
        self.frame_10.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout_2.addWidget(self.frame_10)


        self.verticalLayout_10.addLayout(self.horizontalLayout_2)


        self.verticalLayout_8.addLayout(self.verticalLayout_10)


        self.verticalLayout_4.addWidget(self.frame)

        self.frame_2 = QFrame(MainWidget)
        self.frame_2.setObjectName(u"frame_2")
        self.frame_2.setMinimumSize(QSize(0, 2))
        self.frame_2.setMaximumSize(QSize(16777215, 2))
        self.frame_2.setStyleSheet(u"background-color: #474747;")
        self.frame_2.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_4.addWidget(self.frame_2)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.frame_8 = QFrame(MainWidget)
        self.frame_8.setObjectName(u"frame_8")
        self.frame_8.setMinimumSize(QSize(2, 0))
        self.frame_8.setMaximumSize(QSize(2, 16777215))
        self.frame_8.setStyleSheet(u"background-color: #474747;")
        self.frame_8.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout.addWidget(self.frame_8)

        self.drawbar = DRAW_BAR(MainWidget)
        self.drawbar.setObjectName(u"drawbar")
        sizePolicy.setHeightForWidth(self.drawbar.sizePolicy().hasHeightForWidth())
        self.drawbar.setSizePolicy(sizePolicy)
        self.drawbar.setMinimumSize(QSize(60, 0))
        self.drawbar.setMaximumSize(QSize(60, 16777215))
        self.drawbar.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout.addWidget(self.drawbar)

        self.frame_4 = QFrame(MainWidget)
        self.frame_4.setObjectName(u"frame_4")
        self.frame_4.setMinimumSize(QSize(2, 0))
        self.frame_4.setMaximumSize(QSize(2, 16777215))
        self.frame_4.setStyleSheet(u"background-color: #474747;")
        self.frame_4.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout.addWidget(self.frame_4)

        self.chartview = QFrame(MainWidget)
        self.chartview.setObjectName(u"chartview")
        sizePolicy.setHeightForWidth(self.chartview.sizePolicy().hasHeightForWidth())
        self.chartview.setSizePolicy(sizePolicy)
        self.chartview.setMinimumSize(QSize(1000, 0))
        self.chartview.setStyleSheet(u"")
        self.chartview.setFrameShape(QFrame.NoFrame)
        self.horizontalLayout_3 = QHBoxLayout(self.chartview)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.chartframe = QFrame(self.chartview)
        self.chartframe.setObjectName(u"chartframe")
        sizePolicy.setHeightForWidth(self.chartframe.sizePolicy().hasHeightForWidth())
        self.chartframe.setSizePolicy(sizePolicy)
        self.chartframe.setMinimumSize(QSize(800, 0))
        self.chartframe.setStyleSheet(u"")
        self.chartframe.setFrameShape(QFrame.NoFrame)
        self.verticalLayout_9 = QVBoxLayout(self.chartframe)
        self.verticalLayout_9.setSpacing(0)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.chartframe)
        self.splitter.setObjectName(u"splitter")
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Vertical)
        self.chartbox_splitter = GraphSplitter(self.splitter)
        self.chartbox_splitter.setObjectName(u"chartbox_splitter")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.chartbox_splitter.sizePolicy().hasHeightForWidth())
        self.chartbox_splitter.setSizePolicy(sizePolicy1)
        self.chartbox_splitter.setMinimumSize(QSize(800, 0))
        self.splitter.addWidget(self.chartbox_splitter)
        self.bottom_frame = QWidget(self.splitter)
        self.bottom_frame.setObjectName(u"bottom_frame")
        sizePolicy.setHeightForWidth(self.bottom_frame.sizePolicy().hasHeightForWidth())
        self.bottom_frame.setSizePolicy(sizePolicy)
        self.bottom_frame.setMinimumSize(QSize(0, 90))
        self.bottom_frame.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_7 = QVBoxLayout(self.bottom_frame)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.layout_bottom = QVBoxLayout()
        self.layout_bottom.setSpacing(0)
        self.layout_bottom.setObjectName(u"layout_bottom")

        self.verticalLayout_7.addLayout(self.layout_bottom)

        self.splitter.addWidget(self.bottom_frame)

        self.verticalLayout_9.addWidget(self.splitter)


        self.horizontalLayout_3.addWidget(self.chartframe)

        self.rightview = QFrame(self.chartview)
        self.rightview.setObjectName(u"rightview")
        sizePolicy.setHeightForWidth(self.rightview.sizePolicy().hasHeightForWidth())
        self.rightview.setSizePolicy(sizePolicy)
        self.rightview.setMaximumSize(QSize(0, 16777215))
        self.rightview.setFont(font)
        self.rightview.setStyleSheet(u"")
        self.rightview.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout_3.addWidget(self.rightview)

        self.frame_9 = QFrame(self.chartview)
        self.frame_9.setObjectName(u"frame_9")
        self.frame_9.setMinimumSize(QSize(2, 0))
        self.frame_9.setMaximumSize(QSize(2, 16777215))
        self.frame_9.setStyleSheet(u"background-color: #474747;")
        self.frame_9.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout_3.addWidget(self.frame_9)


        self.horizontalLayout.addWidget(self.chartview)

        self.rightbar = RIGHT_BAR(MainWidget)
        self.rightbar.setObjectName(u"rightbar")
        sizePolicy.setHeightForWidth(self.rightbar.sizePolicy().hasHeightForWidth())
        self.rightbar.setSizePolicy(sizePolicy)
        self.rightbar.setMinimumSize(QSize(60, 0))
        self.rightbar.setMaximumSize(QSize(60, 16777215))
        self.rightbar.setStyleSheet(u"")
        self.rightbar.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout.addWidget(self.rightbar)

        self.frame_7 = QFrame(MainWidget)
        self.frame_7.setObjectName(u"frame_7")
        self.frame_7.setMinimumSize(QSize(2, 0))
        self.frame_7.setMaximumSize(QSize(2, 16777215))
        self.frame_7.setStyleSheet(u"background-color: #474747;")
        self.frame_7.setFrameShape(QFrame.NoFrame)

        self.horizontalLayout.addWidget(self.frame_7)


        self.verticalLayout_4.addLayout(self.horizontalLayout)

        self.frame_5 = QFrame(MainWidget)
        self.frame_5.setObjectName(u"frame_5")
        self.frame_5.setMinimumSize(QSize(0, 2))
        self.frame_5.setMaximumSize(QSize(16777215, 2))
        self.frame_5.setStyleSheet(u"background-color: #474747;")
        self.frame_5.setFrameShape(QFrame.NoFrame)

        self.verticalLayout_4.addWidget(self.frame_5)


        self.verticalLayout.addLayout(self.verticalLayout_4)


        self.retranslateUi(MainWidget)

        QMetaObject.connectSlotsByName(MainWidget)
    # setupUi

    def retranslateUi(self, MainWidget):
        MainWidget.setWindowTitle(QCoreApplication.translate("MainWidget", u"Frame", None))
    # retranslateUi

