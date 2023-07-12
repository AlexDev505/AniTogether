"""

Модуль, в котором реализован интерфейс.

"""


from . import icons_rc
from .found_title import Ui_FoundTitle
from .main import Ui_MainWindow
from .player_controls import Ui_PlayerControls
from .search_result import Ui_SearchResult


__all__ = ["Ui_MainWindow", "Ui_FoundTitle", "Ui_SearchResult", "Ui_PlayerControls"]
