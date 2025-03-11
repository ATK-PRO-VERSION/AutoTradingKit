# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'draw_bar.ui'
##
## Created by: Qt User Interface Compiler version 6.4.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QMetaObject)
from PySide6.QtWidgets import (QSizePolicy, QSpacerItem,
    QVBoxLayout)

class Ui_draw_bar(object):
    def setupUi(self, draw_bar):
        if not draw_bar.objectName():
            draw_bar.setObjectName(u"draw_bar")
        draw_bar.resize(94, 408)
        self.verticalLayout_3 = QVBoxLayout(draw_bar)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(5, 5, 0, 0)
        self._draw_layout = QVBoxLayout()
        self._draw_layout.setSpacing(6)
        self._draw_layout.setObjectName(u"_draw_layout")
        self._draw_layout.setContentsMargins(0, 0, 0, 0)

        self.verticalLayout_3.addLayout(self._draw_layout)

        self.verticalSpacer = QSpacerItem(20, 371, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout_3.addItem(self.verticalSpacer)

        self._setting_layout = QVBoxLayout()
        self._setting_layout.setSpacing(0)
        self._setting_layout.setObjectName(u"_setting_layout")

        self.verticalLayout_3.addLayout(self._setting_layout)


        self.retranslateUi(draw_bar)

        QMetaObject.connectSlotsByName(draw_bar)
    # setupUi

    def retranslateUi(self, draw_bar):
        draw_bar.setWindowTitle(QCoreApplication.translate("draw_bar", u"Frame", None))
    # retranslateUi

