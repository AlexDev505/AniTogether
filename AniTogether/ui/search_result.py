from functools import partial

from PyQt6 import QtCore, QtGui, QtWidgets


class TitleWidget(QtWidgets.QFrame):
    titleChanged = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.titleWidgetLayout = QtWidgets.QHBoxLayout(self)
        self.titleWidgetLayout.setContentsMargins(10, 4, 10, 4)
        self.titleWidgetLayout.setSpacing(10)
        self.titleIcon = QtWidgets.QLabel(self)
        self.titleIcon.setMinimumSize(50, 50)
        self.titleLabel = QtWidgets.QLabel(self)
        self.titleLabel.setSizePolicy(
            QtWidgets.QSizePolicy(
                QtWidgets.QSizePolicy.Policy.Expanding,
                QtWidgets.QSizePolicy.Policy.Minimum,
            )
        )
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(14)
        font.setBold(True)
        self.titleLabel.setFont(font)
        self.titleWidgetLayout.addWidget(self.titleIcon)
        self.titleWidgetLayout.addWidget(self.titleLabel)

    def setTitle(self, title: str) -> None:
        self.titleLabel.setText(title)
        self.titleChanged.emit()


class SearchResultWidget(QtWidgets.QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("searchResultFrame")
        self.setStyleSheet(
            """
        QFrame {
            background-color: rgb(30,30,30);
        }
        QFrame * {
            border: none;
            background-color: transparent;
            color: rgb(255,255,255);
        }
        QFrame QWidget QFrame:hover {
            background-color: rgb(48,48,48);
        }
        /*SCROLLBAR */
        /* VERTICAL SCROLLBAR */
        QScrollBar:vertical {
            border: none;
            width: 8px;
        }
        /* HANDLE BAR VERTICAL */
        QScrollBar::handle:vertical {
            background-color: rgb(53,53,53);
            min-height: 30px;
        }
        /* BTN TOP */
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
        /* BTN BOTTOM */
        QScrollBar::add-line:vertical {
            height: 0px;
        }
        /* RESET ARROW */
        QScrollBar::up-arrow:vertical
        QScrollBar::down-arrow:vertical,
        QScrollBar::add-page:vertical,
        QScrollBar::sub-page:vertical {
            background: transparent;
        }
        """
        )

        self.setMaximumHeight(330)

        self.searchResultWidgetLayout = QtWidgets.QVBoxLayout(self)
        self.searchResultWidgetLayout.setContentsMargins(0, 0, 0, 0)

        self.scrollArea = QtWidgets.QScrollArea(self)
        self.scrollArea.setWidgetResizable(True)
        self.scrollAreaContainer = QtWidgets.QWidget()
        self.scrollAreaContainerLayout = QtWidgets.QVBoxLayout(self.scrollAreaContainer)
        self.scrollAreaContainerLayout.setContentsMargins(0, 0, 0, 0)
        self.scrollAreaContainerLayout.setSpacing(0)
        self.scrollArea.setWidget(self.scrollAreaContainer)
        self.scrollArea.verticalScrollBar().setSingleStep(10)

        self.scrollArea.setMaximumHeight(330)

        self.searchResultWidgetLayout.addWidget(self.scrollArea)

        QtCore.QMetaObject.connectSlotsByName(self)

    def addTitle(self) -> TitleWidget:
        title_widget = TitleWidget(self.scrollAreaContainer)
        self.scrollAreaContainerLayout.addWidget(title_widget)
        title_widget.titleChanged.connect(partial(self._check_new_width, title_widget))
        title_widget_height = title_widget.sizeHint().height() + 8
        if self.minimumHeight() + title_widget_height < 300:
            self.setMinimumHeight(self.minimumHeight() + title_widget_height)
        return title_widget

    def _check_new_width(self, title_widget: TitleWidget) -> None:
        title_widget.titleChanged.disconnect()
        while title_widget.sizeHint().width() + 20 > self.parent().width() - 100:
            title_widget.titleLabel.setText(title_widget.titleLabel.text()[:-4] + "...")
        self.setMinimumWidth(
            max(self.minimumWidth(), title_widget.sizeHint().width() + 20)
        )

    def delete(self):
        self.hide()
        self.deleteLater()
