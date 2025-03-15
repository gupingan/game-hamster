# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'view.ui'
##
## Created by: Qt User Interface Compiler version 5.15.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1057, 601)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(-1, 9, -1, -1)
        self.logoWidget = QWidget(self.centralwidget)
        self.logoWidget.setObjectName(u"logoWidget")
        self.horizontalLayout_2 = QHBoxLayout(self.logoWidget)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_3)

        self.bannerLogo = QLabel(self.logoWidget)
        self.bannerLogo.setObjectName(u"bannerLogo")
        self.bannerLogo.setMaximumSize(QSize(16777215, 16777215))
        self.bannerLogo.setScaledContents(False)
        self.bannerLogo.setAlignment(Qt.AlignCenter)
        self.bannerLogo.setMargin(0)

        self.horizontalLayout_2.addWidget(self.bannerLogo)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


        self.verticalLayout.addWidget(self.logoWidget)

        self.logoTableHeight = QWidget(self.centralwidget)
        self.logoTableHeight.setObjectName(u"logoTableHeight")

        self.verticalLayout.addWidget(self.logoTableHeight)

        self.tableView = QTableView(self.centralwidget)
        self.tableView.setObjectName(u"tableView")

        self.verticalLayout.addWidget(self.tableView)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 5, -1, -1)
        self.totalProgressBar = QProgressBar(self.centralwidget)
        self.totalProgressBar.setObjectName(u"totalProgressBar")
        self.totalProgressBar.setMaximumSize(QSize(166, 22))
        self.totalProgressBar.setStyleSheet(u"")
        self.totalProgressBar.setValue(0)
        self.totalProgressBar.setTextVisible(False)

        self.horizontalLayout.addWidget(self.totalProgressBar)

        self.bottomHint = QLabel(self.centralwidget)
        self.bottomHint.setObjectName(u"bottomHint")

        self.horizontalLayout.addWidget(self.bottomHint)

        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.toggleStateBtn = QPushButton(self.centralwidget)
        self.toggleStateBtn.setObjectName(u"toggleStateBtn")
        self.toggleStateBtn.setMinimumSize(QSize(99, 30))

        self.horizontalLayout.addWidget(self.toggleStateBtn)


        self.verticalLayout.addLayout(self.horizontalLayout)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"\u6e38\u620f\u4ed3\u9f20 (\u6587\u4ef6\u5b8c\u6574\u6027\u6821\u9a8c)", None))
        self.bannerLogo.setText(QCoreApplication.translate("MainWindow", u"Banner Logo \u672a\u8bbe\u7f6e", None))
        self.bottomHint.setText(QCoreApplication.translate("MainWindow", u"\u8fd9\u91cc\u662f\u5e95\u90e8\u63d0\u793a", None))
        self.toggleStateBtn.setText(QCoreApplication.translate("MainWindow", u"\u5f00\u59cb\u6821\u9a8c", None))
    # retranslateUi

