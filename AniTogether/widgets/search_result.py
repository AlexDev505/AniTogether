from functools import partial

from PyQt6.QtWidgets import QFrame

from ui import Ui_SearchResult
from .found_title import FoundTitleWidget


class SearchResultWidget(QFrame, Ui_SearchResult):
    ITEMS_PER_PAGE = 5

    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.setParent(parent)

        self.scrollArea.verticalScrollBar().setSingleStep(10)

        self.max_title_widget_width: int = 0
        self._deleted = False

        self.initMaxHeight()

    def addTitle(self) -> FoundTitleWidget:
        """
        Создает пустой виджет релиза и возвращает его.
        :return: Пустой виджет релиза.
        """
        foundTitleWidget = FoundTitleWidget(self.scrollAreaContainer)
        self.scrollAreaContainerLayout.addWidget(foundTitleWidget)
        foundTitleWidget.titleChanged.connect(
            partial(self._check_max_title_widget_width, foundTitleWidget)
        )

        # FoundTitleWidget.widgetHeight вычисляется
        # только при первой инициализации FoundTitleWidget
        self.initMaxHeight()

        # Увеличиваем высоту виджета для отображения нового элемента
        height_with_new_widget = self.minimumHeight() + FoundTitleWidget.widgetHeight
        # Пока превышает максимальный размер
        if height_with_new_widget < self.scrollArea.maximumHeight():
            self.setMinimumHeight(height_with_new_widget)
        return foundTitleWidget

    def _check_max_title_widget_width(self, foundTitleWidget: FoundTitleWidget) -> None:
        self.max_title_widget_width = max(
            self.max_title_widget_width,
            foundTitleWidget.sizeHint().width() + FoundTitleWidget.hMargin * 2,
        )
        self.setWidth(self.max_title_widget_width)

    def setWidth(self, width: int) -> None:
        # Вызов функции в QTimer, может наткнуться на удаленный виджет
        if self._deleted:
            return
        rect = self.geometry()
        rect.setWidth(width)
        self.setGeometry(rect)
        titleWidget: FoundTitleWidget
        for titleWidget in self.scrollAreaContainer.children():
            if type(titleWidget) is FoundTitleWidget:
                titleWidget.setFixedWidth(min(width, self.maximumWidth()))

    def initMaxHeight(self) -> None:
        """
        Устанавливает максимальную высоту виджета.
        """
        if self.scrollArea.maximumHeight() == 0:
            self.scrollArea.setMaximumHeight(
                FoundTitleWidget.widgetHeight * (self.ITEMS_PER_PAGE + 1)
            )

    def delete(self) -> None:
        """
        Удаляет виджет.
        """
        self._deleted = True
        self.hide()
        self.deleteLater()
