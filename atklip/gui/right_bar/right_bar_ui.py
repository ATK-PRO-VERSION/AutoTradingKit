# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'right_bar.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtWidgets import (QSizePolicy, QSpacerItem,
    QVBoxLayout)

class Ui_right_bar(object):
    def setupUi(self, right_bar):
        if not right_bar.objectName():
            right_bar.setObjectName(u"right_bar")
        right_bar.resize(94, 432)
        self.verticalLayout_3 = QVBoxLayout(right_bar)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 5, 5, 0)
        self._draw_layout = QVBoxLayout()
        self._draw_layout.setSpacing(0)
        self._draw_layout.setObjectName(u"_draw_layout")

        self.verticalLayout_3.addLayout(self._draw_layout)

        self.verticalSpacer = QSpacerItem(20, 371, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self._setting_layout = QVBoxLayout()
        self._setting_layout.setSpacing(0)
        self._setting_layout.setObjectName(u"_setting_layout")

        self.verticalLayout_3.addLayout(self._setting_layout)


        self.retranslateUi(right_bar)

        QMetaObject.connectSlotsByName(right_bar)
    # setupUi

    def retranslateUi(self, right_bar):
        right_bar.setWindowTitle(QCoreApplication.translate("right_bar", u"Frame", None))
    # retranslateUi

