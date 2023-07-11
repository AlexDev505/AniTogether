from functools import partial

from PyQt6 import QtCore, QtGui, QtWidgets


class TitleWidget(QtWidgets.QFrame):
    h_margin = 20
    v_margin = 6
    spacing = 15
    icon_size = 40

    widget_height = icon_size + v_margin * 2

    titleChanged = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)

        self.setObjectName("titleWidget")

        self.titleWidgetLayout = QtWidgets.QHBoxLayout(self)
        self.titleWidgetLayout.setContentsMargins(
            TitleWidget.h_margin,
            TitleWidget.v_margin,
            TitleWidget.h_margin,
            TitleWidget.v_margin,
        )
        self.titleWidgetLayout.setSpacing(TitleWidget.spacing)
        self.titleIcon = QtWidgets.QLabel(self)
        self.titleIcon.setObjectName("titleIcon")
        self.titleIcon.setMinimumSize(TitleWidget.icon_size, TitleWidget.icon_size)
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
        #titleWidget:hover {
            background-color: rgb(48,48,48);
        }
        #titleWidget #titleIcon {
            background-color: rgb(37,37,37);
            border-radius: 20px;
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

        self.scrollArea.setMaximumHeight(TitleWidget.widget_height * 6)

        self.searchResultWidgetLayout.addWidget(self.scrollArea)

        QtCore.QMetaObject.connectSlotsByName(self)

    def addTitle(self) -> TitleWidget:
        title_widget = TitleWidget(self.scrollAreaContainer)
        self.scrollAreaContainerLayout.addWidget(title_widget)
        title_widget.titleChanged.connect(partial(self._check_new_width, title_widget))
        title_widget_height = TitleWidget.widget_height
        if self.minimumHeight() + title_widget_height < self.scrollArea.maximumHeight():
            self.setMinimumHeight(self.minimumHeight() + title_widget_height)
        return title_widget

    def _check_new_width(self, title_widget: TitleWidget) -> None:
        title_widget.titleChanged.disconnect()
        while (
            title_widget.sizeHint().width() + TitleWidget.h_margin * 2
            > self.parent().width() - 100
        ):
            title_widget.titleLabel.setText(title_widget.titleLabel.text()[:-4] + "...")
        self.setMinimumWidth(
            max(
                self.minimumWidth(),
                title_widget.sizeHint().width() + TitleWidget.h_margin * 2,
            )
        )

    def delete(self):
        self.hide()
        self.deleteLater()
