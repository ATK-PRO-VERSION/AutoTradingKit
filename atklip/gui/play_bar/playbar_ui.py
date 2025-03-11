# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'playbar.ui'
##
## Created by: Qt User Interface Compiler version 6.8.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject, QSize)
from PySide6.QtWidgets import (QFrame, QHBoxLayout, QSizePolicy,
    QSpacerItem, QVBoxLayout)

class Ui_Frame(object):
    def setupUi(self, Frame):
        if not Frame.objectName():
            Frame.setObjectName(u"Frame")
        Frame.resize(691, 52)
        self.verticalLayout = QVBoxLayout(Frame)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame_3 = QFrame(Frame)
        self.frame_3.setObjectName(u"frame_3")
        self.frame_3.setMinimumSize(QSize(0, 2))
        self.frame_3.setMaximumSize(QSize(16777215, 2))
        self.frame_3.setStyleSheet(u"background-color: #474747;")
        self.frame_3.setFrameShape(QFrame.NoFrame)

        self.verticalLayout.addWidget(self.frame_3)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer = QSpacerItem(380, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer)

        self.center_layout = QHBoxLayout()
        self.center_layout.setSpacing(5)
        self.center_layout.setObjectName(u"center_layout")
        self.center_layout.setContentsMargins(0, 0, 0, 0)

        self.horizontalLayout_2.addLayout(self.center_layout)

        self.horizontalSpacer_2 = QSpacerItem(380, 40, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)

        self.right_layout = QHBoxLayout()
        self.right_layout.setSpacing(5)
        self.right_layout.setObjectName(u"right_layout")
        self.right_layout.setContentsMargins(0, 0, 5, 0)

        self.horizontalLayout_2.addLayout(self.right_layout)


        self.verticalLayout.addLayout(self.horizontalLayout_2)


        self.retranslateUi(Frame)

        QMetaObject.connectSlotsByName(Frame)
    # setupUi

    def retranslateUi(self, Frame):
        Frame.setWindowTitle(QCoreApplication.translate("Frame", u"Frame", None))
    # retranslateUi

