from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableView, QPushButton,
    QHeaderView, QMessageBox, QAbstractItemView
)
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex, Signal
from PySide6.QtGui import QColor

from ..models.attribute import Attribute
from ..models.dictionary import Dictionary
from ..utils.constants import DATA_TYPES


class DictionaryTableModel(QAbstractTableModel):
    """Table model for the data dictionary."""

    COLUMNS = ["Name", "Type", "Size", "Primary Key"]

    def __init__(self, dictionary: Dictionary, parent=None):
        super().__init__(parent)
        self._dictionary = dictionary
        self._attribute_list: list[Attribute] = []
        self.refresh()

    def set_dictionary(self, dictionary: Dictionary):
        """Set a new dictionary and refresh."""
        self._dictionary = dictionary
        self.refresh()

    def refresh(self):
        """Refresh the model from the dictionary."""
        self.beginResetModel()
        self._attribute_list = self._dictionary.get_all_attributes()
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()) -> int:
        return len(self._attribute_list)

    def columnCount(self, parent=QModelIndex()) -> int:
        return len(self.COLUMNS)

    def headerData(self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.COLUMNS[section]
        return None

    def data(self, index: QModelIndex, role=Qt.DisplayRole):
        if not index.isValid() or index.row() >= len(self._attribute_list):
            return None

        attr = self._attribute_list[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                return attr.name
            elif col == 1:
                return attr.data_type
            elif col == 2:
                return str(attr.size) if attr.size else ""
            elif col == 3:
                return "Yes" if attr.is_primary_key else "No"

        elif role == Qt.BackgroundRole:
            if attr.is_primary_key:
                return QColor("#FFFDE7")  # Light yellow for PKs

        elif role == Qt.TextAlignmentRole:
            if col in (2, 3):
                return Qt.AlignCenter

        return None

    def get_attribute_at(self, row: int) -> Attribute | None:
        """Get the attribute at a specific row."""
        if 0 <= row < len(self._attribute_list):
            return self._attribute_list[row]
        return None


class DictionaryView(QWidget):
    """View for managing the data dictionary."""

    attribute_changed = Signal()  # Emitted when dictionary changes

    def __init__(self, dictionary: Dictionary, parent=None):
        super().__init__(parent)
        self._dictionary = dictionary
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Toolbar
        toolbar = QHBoxLayout()

        self._add_btn = QPushButton("Add Attribute")
        self._add_btn.clicked.connect(self._on_add)
        toolbar.addWidget(self._add_btn)

        self._edit_btn = QPushButton("Edit")
        self._edit_btn.clicked.connect(self._on_edit)
        toolbar.addWidget(self._edit_btn)

        self._delete_btn = QPushButton("Delete")
        self._delete_btn.clicked.connect(self._on_delete)
        toolbar.addWidget(self._delete_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # Table view
        self._model = DictionaryTableModel(self._dictionary)
        self._table = QTableView()
        self._table.setModel(self._model)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.setSelectionMode(QAbstractItemView.SingleSelection)
        self._table.setAlternatingRowColors(True)
        self._table.doubleClicked.connect(self._on_edit)

        # Configure header
        header = self._table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)

        layout.addWidget(self._table)

    def set_dictionary(self, dictionary: Dictionary):
        """Set a new dictionary and refresh the view."""
        self._dictionary = dictionary
        self._model.set_dictionary(dictionary)

    def refresh(self):
        """Refresh the view from the dictionary."""
        self._model.refresh()

    def _get_selected_row(self) -> int:
        """Get the currently selected row index, or -1 if none."""
        indexes = self._table.selectionModel().selectedRows()
        if indexes:
            return indexes[0].row()
        return -1

    def _on_add(self):
        """Handle add button click."""
        from .dialogs.attribute_dialog import AttributeDialog

        dialog = AttributeDialog(self._dictionary, parent=self)
        if dialog.exec():
            attr = dialog.get_attribute()
            if attr:
                if self._dictionary.add_attribute(attr):
                    self._model.refresh()
                    self.attribute_changed.emit()
                else:
                    QMessageBox.warning(
                        self, "Error",
                        f"Attribute '{attr.name}' already exists."
                    )

    def _on_edit(self):
        """Handle edit button click."""
        row = self._get_selected_row()
        if row < 0:
            QMessageBox.information(self, "Info", "Please select an attribute to edit.")
            return

        attr = self._model.get_attribute_at(row)
        if not attr:
            return

        from .dialogs.attribute_dialog import AttributeDialog

        dialog = AttributeDialog(self._dictionary, attribute=attr, parent=self)
        if dialog.exec():
            new_attr = dialog.get_attribute()
            if new_attr:
                if self._dictionary.update_attribute(attr.name, new_attr):
                    self._model.refresh()
                    self.attribute_changed.emit()
                else:
                    QMessageBox.warning(
                        self, "Error",
                        f"Could not update attribute. Name '{new_attr.name}' may already exist."
                    )

    def _on_delete(self):
        """Handle delete button click."""
        row = self._get_selected_row()
        if row < 0:
            QMessageBox.information(self, "Info", "Please select an attribute to delete.")
            return

        attr = self._model.get_attribute_at(row)
        if not attr:
            return

        result = QMessageBox.question(
            self, "Confirm Delete",
            f"Are you sure you want to delete attribute '{attr.name}'?\n"
            "This may affect entities using this attribute.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if result == QMessageBox.Yes:
            self._dictionary.remove_attribute(attr.name)
            self._model.refresh()
            self.attribute_changed.emit()
