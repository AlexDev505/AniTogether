# Form implementation generated from reading ui file 'interface\search_result.ui'
#
# Created by: PyQt6 UI code generator 6.5.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic6 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt6 import QtCore, QtWidgets


class Ui_SearchResult(object):
    def setupUi(self, SearchResult):
        SearchResult.setObjectName("SearchResult")
        SearchResult.resize(94, 63)
        SearchResult.setStyleSheet(
            "* {border: none;color: rgb(255,255,255)}\n"
            "#SearchResult {background-color: rgb(30,30,30)}\n"
            "#SearchResult * {background-color: transparent}\n"
            "/* VERTICAL SCROLLBAR */\n"
            "QScrollBar:vertical {border: none;width: 8px}\n"
            "/* HANDLE BAR VERTICAL */\n"
            "QScrollBar::handle:vertical {\n"
            "    background-color: rgb(53,53,53);\n"
            "    min-height: 30px\n"
            "}\n"
            "/* BTN TOP */\n"
            "QScrollBar::sub-line:vertical {height: 0px}\n"
            "/* BTN BOTTOM */\n"
            "QScrollBar::add-line:vertical {height: 0px}\n"
            "/* RESET ARROW */\n"
            "QScrollBar::up-arrow:vertical\n"
            "QScrollBar::down-arrow:vertical,\n"
            "QScrollBar::add-page:vertical,\n"
            "QScrollBar::sub-page:vertical {\n"
            "    background: transparent\n"
            "}"
        )
        self.verticalLayout = QtWidgets.QVBoxLayout(SearchResult)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.scrollArea = QtWidgets.QScrollArea(parent=SearchResult)
        self.scrollArea.setMaximumSize(QtCore.QSize(16777215, 0))
        self.scrollArea.setHorizontalScrollBarPolicy(
            QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setObjectName("scrollArea")
        self.scrollAreaContainer = QtWidgets.QWidget()
        self.scrollAreaContainer.setGeometry(QtCore.QRect(0, 0, 86, 16))
        self.scrollAreaContainer.setObjectName("scrollAreaContainer")
        self.scrollAreaContainerLayout = QtWidgets.QVBoxLayout(self.scrollAreaContainer)
        self.scrollAreaContainerLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaContainerLayout.setSpacing(0)
        self.scrollAreaContainerLayout.setObjectName("scrollAreaContainerLayout")
        self.scrollArea.setWidget(self.scrollAreaContainer)
        self.verticalLayout.addWidget(self.scrollArea)

        self.retranslateUi(SearchResult)
        QtCore.QMetaObject.connectSlotsByName(SearchResult)

    def retranslateUi(self, SearchResult):
        pass
