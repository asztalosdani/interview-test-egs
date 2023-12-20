import sys

from PySide6.QtCore import Qt, QAbstractTableModel
from PySide6.QtGui import QKeyEvent, QColor
from PySide6.QtWidgets import QApplication, QDialog, QHBoxLayout, QVBoxLayout, QTableView, QPushButton, QAbstractItemView, QHeaderView, QMessageBox

from bowling_tracker.bowling_score_tracker import BowlingScoreTracker, Shot, ShotInvalidException

HIGHLIGHT_COLOR = QColor("#9EA4B4")
BACKGROUND_COLOR = QColor("#E2E8F8")


class BowlingScoreTableModel(QAbstractTableModel):

    def __init__(self, parent, bowling_score_tracker: BowlingScoreTracker):
        super().__init__(parent)
        self._bowling_score_tracker = bowling_score_tracker
        self._frames = []
        self._scores = []
        self.update()

    def rowCount(self, parent=...):
        return 2

    def columnCount(self, parent=...):
        return 10

    def data(self, index, role=...):
        row = index.row()
        column = index.column()

        if role == Qt.DisplayRole:
            if row == 0:
                if column > len(self._frames) - 1:
                    return ""

                shots = self._frames[column]
                if len(shots) == 1 and shots[0] is Shot.STRIKE:
                    return f"{shots[0].value} | _"
                else:
                    return " | ".join(str(shot.value) for shot in shots)
            else:

                if column > len(self._scores) - 1:
                    return None

                return self._scores[column]

        if role == Qt.ItemDataRole.TextAlignmentRole:
            return Qt.AlignmentFlag.AlignCenter

        if role == Qt.ItemDataRole.BackgroundRole:
            if row == 0:
                if column == self._bowling_score_tracker.current_frame:
                    return HIGHLIGHT_COLOR
                else:
                    return BACKGROUND_COLOR

    def headerData(self, section, orientation, role=...):
        if orientation == Qt.Orientation.Horizontal:
            return super().headerData(section, orientation, role)
        else:
            return None

    def update(self):
        self.beginResetModel()
        self._scores = self._bowling_score_tracker.get_scores()
        self._frames = self._bowling_score_tracker.get_shots_by_frame()
        self.endResetModel()


class BowlingScoreTrackerDialog(QDialog):

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bowling Score Tracker")
        self.setFixedSize(500, 130)
        self.grabKeyboard()

        self._bowling_score_tracker = BowlingScoreTracker()
        self._table_model = BowlingScoreTableModel(self, self._bowling_score_tracker)

        main_layout = QVBoxLayout(self)

        self._table_view = QTableView(self)
        main_layout.addWidget(self._table_view)
        self._table_view.setModel(self._table_model)
        self._table_view.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self._table_view.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self._table_view.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        button_layout = QHBoxLayout(self)
        main_layout.addLayout(button_layout)
        button_layout.addStretch()

        self._reset_button = QPushButton("Reset")
        button_layout.addWidget(self._reset_button)
        self._reset_button.clicked.connect(self._on_reset_clicked)

    def _on_reset_clicked(self):
        self._bowling_score_tracker.reset()
        self._table_model.update()

    def keyPressEvent(self, key_event: QKeyEvent):
        if key_event.isAutoRepeat():
            return

        if self._bowling_score_tracker.game_over:
            return

        text = key_event.text()
        if shot := Shot.from_string(text):
            try:
                self._bowling_score_tracker.shoot(shot)
                self._table_model.update()
            except ShotInvalidException as e:
                self.releaseKeyboard()
                QMessageBox.critical(self, "Error", f"Invalid shot: {e.shot.value}")
                self.grabKeyboard()


def main():
    app = QApplication(sys.argv)
    dialog = BowlingScoreTrackerDialog()
    dialog.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
