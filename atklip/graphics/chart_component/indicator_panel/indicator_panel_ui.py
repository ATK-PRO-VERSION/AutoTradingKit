# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'indicator_panel.ui'
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
from PySide6.QtWidgets import (QApplication, QFrame, QHBoxLayout, QLabel,
    QPushButton, QSizePolicy, QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(303, 28)
        Form.setMinimumSize(QSize(0, 28))
        Form.setMaximumSize(QSize(16777215, 28))
        Form.setStyleSheet(u"")
        self.horizontalLayout = QHBoxLayout(Form)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.frame = QFrame(Form)
        self.frame.setObjectName(u"frame")
        self.frame.setMinimumSize(QSize(0, 28))
        self.frame.setMaximumSize(QSize(16777215, 28))
        self.frame.setStyleSheet(u"")
        self.frame.setFrameShape(QFrame.Shape.NoFrame)
        self.frame.setFrameShadow(QFrame.Shadow.Plain)
        self.horizontalLayout_2 = QHBoxLayout(self.frame)
        self.horizontalLayout_2.setSpacing(5)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(10, 0, 2, 0)
        self.name = QLabel(self.frame)
        self.name.setObjectName(u"name")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.name.sizePolicy().hasHeightForWidth())
        self.name.setSizePolicy(sizePolicy)
        self.name.setMinimumSize(QSize(0, 25))
        self.name.setMaximumSize(QSize(16777215, 25))
        font = QFont()
        font.setFamilies([u"Segoe UI"])
        font.setPointSize(10)
        font.setBold(False)
        font.setItalic(False)
        font.setStyleStrategy(QFont.PreferAntialias)
        self.name.setFont(font)
        self.name.setStyleSheet(u"")
        self.name.setScaledContents(True)
        self.name.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignVCenter)
        self.name.setWordWrap(False)
        self.name.setMargin(0)

        self.horizontalLayout_2.addWidget(self.name)

        self.showhide = QPushButton(self.frame)
        self.showhide.setObjectName(u"showhide")
        sizePolicy.setHeightForWidth(self.showhide.sizePolicy().hasHeightForWidth())
        self.showhide.setSizePolicy(sizePolicy)
        self.showhide.setMinimumSize(QSize(25, 25))
        self.showhide.setMaximumSize(QSize(25, 25))
        self.showhide.setStyleSheet(u"")
        icon = QIcon()
        icon.addFile(u":/qfluentwidgets/images/icons/eye_drawing.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.showhide.setIcon(icon)
        self.showhide.setFlat(True)

        self.horizontalLayout_2.addWidget(self.showhide)

        self.btn_indicator_setting = QPushButton(self.frame)
        self.btn_indicator_setting.setObjectName(u"btn_indicator_setting")
        sizePolicy.setHeightForWidth(self.btn_indicator_setting.sizePolicy().hasHeightForWidth())
        self.btn_indicator_setting.setSizePolicy(sizePolicy)
        self.btn_indicator_setting.setMinimumSize(QSize(25, 25))
        self.btn_indicator_setting.setMaximumSize(QSize(25, 25))
        self.btn_indicator_setting.setStyleSheet(u"")
        icon1 = QIcon()
        icon1.addFile(u":/qfluentwidgets/images/icons/Setting_white.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_indicator_setting.setIcon(icon1)
        self.btn_indicator_setting.setIconSize(QSize(16, 16))
        self.btn_indicator_setting.setFlat(True)

        self.horizontalLayout_2.addWidget(self.btn_indicator_setting)

        self.btn_indicator_close = QPushButton(self.frame)
        self.btn_indicator_close.setObjectName(u"btn_indicator_close")
        sizePolicy.setHeightForWidth(self.btn_indicator_close.sizePolicy().hasHeightForWidth())
        self.btn_indicator_close.setSizePolicy(sizePolicy)
        self.btn_indicator_close.setMinimumSize(QSize(25, 25))
        self.btn_indicator_close.setMaximumSize(QSize(25, 25))
        self.btn_indicator_close.setStyleSheet(u"")
        icon2 = QIcon()
        icon2.addFile(u":/qfluentwidgets/images/icons/Close_white.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_indicator_close.setIcon(icon2)
        self.btn_indicator_close.setIconSize(QSize(12, 12))
        self.btn_indicator_close.setAutoDefault(False)
        self.btn_indicator_close.setFlat(True)

        self.horizontalLayout_2.addWidget(self.btn_indicator_close)

        self.btn_more_option = QPushButton(self.frame)
        self.btn_more_option.setObjectName(u"btn_more_option")
        sizePolicy.setHeightForWidth(self.btn_more_option.sizePolicy().hasHeightForWidth())
        self.btn_more_option.setSizePolicy(sizePolicy)
        self.btn_more_option.setMinimumSize(QSize(25, 25))
        self.btn_more_option.setMaximumSize(QSize(25, 25))
        self.btn_more_option.setStyleSheet(u"")
        icon3 = QIcon()
        icon3.addFile(u":/qfluentwidgets/images/icons/More_white.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.btn_more_option.setIcon(icon3)
        self.btn_more_option.setFlat(True)

        self.horizontalLayout_2.addWidget(self.btn_more_option)


        self.horizontalLayout.addWidget(self.frame)


        self.retranslateUi(Form)

        self.btn_indicator_close.setDefault(False)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.name.setText(QCoreApplication.translate("Form", u"name_indicator", None))
        self.showhide.setText("")
        self.btn_indicator_setting.setText("")
        self.btn_indicator_close.setText("")
        self.btn_more_option.setText("")
    # retranslateUi

