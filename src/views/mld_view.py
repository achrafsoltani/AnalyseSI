from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem,
    QPushButton, QLabel, QHeaderView, QMenu, QInputDialog
)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor, QBrush, QAction

from ..models.project import Project
from ..controllers.mld_transformer import MLDTransformer


class MLDView(QWidget):
    """View for displaying the Logical Data Model (MLD)."""

    # Signal emitted when MLD is modified
    mld_modified = Signal()

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self._project = project
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Header
        header_layout = QHBoxLayout()
        header_label = QLabel("Logical Data Model (MLD)")
        header_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        header_layout.addWidget(header_label)

        header_layout.addStretch()

        # Legend
        legend = QLabel(
            "<span style='color: #1976D2;'>■</span> Primary Key  "
            "<span style='color: #F57C00;'>■</span> Foreign Key  "
            "<span style='color: #666;'>■</span> Regular Column"
        )
        header_layout.addWidget(legend)

        layout.addLayout(header_layout)

        # Tree widget for displaying tables
        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(["Name", "Type", "Constraints", "References"])
        self._tree.setAlternatingRowColors(True)
        self._tree.setRootIsDecorated(True)
        self._tree.setIndentation(20)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._show_context_menu)

        # Configure header
        header = self._tree.header()
        header.setSectionResizeMode(0, QHeaderView.Interactive)
        header.setSectionResizeMode(1, QHeaderView.Interactive)
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.Stretch)
        header.resizeSection(0, 250)
        header.resizeSection(1, 100)
        header.resizeSection(2, 120)

        # Set font
        font = QFont()
        font.setPointSize(10)
        self._tree.setFont(font)

        layout.addWidget(self._tree)

        # Statistics label
        self._stats_label = QLabel()
        self._stats_label.setStyleSheet("color: gray;")
        layout.addWidget(self._stats_label)

        # Hint label
        hint_label = QLabel("Right-click a column to rename it")
        hint_label.setStyleSheet("color: gray; font-style: italic;")
        layout.addWidget(hint_label)

    def _connect_signals(self):
        """Connect signals."""
        self._tree.itemDoubleClicked.connect(self._on_item_double_clicked)

    def _show_context_menu(self, position):
        """Show context menu for renaming columns."""
        item = self._tree.itemAt(position)
        if not item or not item.parent():
            return  # Only show menu for column items (not table headers)

        menu = QMenu(self)
        rename_action = QAction("Rename Column", self)
        rename_action.triggered.connect(lambda: self._rename_column(item))
        menu.addAction(rename_action)
        menu.exec(self._tree.viewport().mapToGlobal(position))

    def _on_item_double_clicked(self, item: QTreeWidgetItem, column: int):
        """Handle double-click to rename."""
        if item.parent() and column == 0:
            self._rename_column(item)

    def _rename_column(self, item: QTreeWidgetItem):
        """Rename a column via dialog."""
        parent = item.parent()
        if not parent:
            return

        table_name = parent.text(0)
        original_name = item.data(0, Qt.UserRole)
        current_name = item.text(0)

        dialog = QInputDialog(self)
        dialog.setWindowTitle("Rename Column")
        dialog.setLabelText(f"Enter new name for column '{current_name}':")
        dialog.setTextValue(current_name)
        dialog.resize(400, dialog.sizeHint().height())

        if dialog.exec() and dialog.textValue().strip() != current_name:
            new_name = dialog.textValue().strip()
            if new_name:
                # Update the display
                item.setText(0, new_name)
                # Save the override
                self._project.set_mld_column_name(table_name, original_name, new_name)
                self.mld_modified.emit()

    def set_project(self, project: Project):
        """Set a new project."""
        self._project = project
        self._tree.clear()
        self._stats_label.clear()

    def generate_mld(self):
        """Generate and display the MLD."""
        self._tree.clear()

        transformer = MLDTransformer(self._project)
        tables = transformer.transform()

        if not tables:
            self._stats_label.setText("No tables to display. Create entities in the MCD first.")
            return

        # Colors for different column types
        pk_color = QColor("#1976D2")  # Blue
        fk_color = QColor("#F57C00")  # Orange
        regular_color = QColor("#333333")  # Dark gray

        table_count = 0
        column_count = 0
        pk_count = 0
        fk_count = 0

        for table in tables:
            table_count += 1

            # Create table item
            table_item = QTreeWidgetItem()
            table_item.setText(0, table.name.upper())
            table_item.setText(1, f"({table.source_type})")

            # Style table header
            bold_font = QFont()
            bold_font.setBold(True)
            bold_font.setPointSize(11)
            table_item.setFont(0, bold_font)

            if table.source_type == "association":
                table_item.setForeground(0, QBrush(fk_color))
            else:
                table_item.setForeground(0, QBrush(pk_color))

            self._tree.addTopLevelItem(table_item)

            # Add columns
            for column in table.columns:
                column_count += 1
                col_item = QTreeWidgetItem()

                # Get display name (may be overridden)
                original_name = column.name
                display_name = self._project.get_mld_column_name(table.name.upper(), original_name)

                col_item.setText(0, display_name)
                col_item.setData(0, Qt.UserRole, original_name)  # Store original for reference
                col_item.setText(1, column.data_type)

                # Build constraints string
                constraints = []
                if column.is_primary_key:
                    constraints.append("PK")
                    pk_count += 1
                if column.is_foreign_key:
                    constraints.append("FK")
                    fk_count += 1
                if not column.is_nullable:
                    constraints.append("NOT NULL")

                col_item.setText(2, ", ".join(constraints) if constraints else "")

                # References
                if column.references_table:
                    col_item.setText(3, f"→ {column.references_table}.{column.references_column}")

                # Color based on type
                if column.is_primary_key:
                    col_item.setForeground(0, QBrush(pk_color))
                    col_item.setForeground(2, QBrush(pk_color))
                elif column.is_foreign_key:
                    col_item.setForeground(0, QBrush(fk_color))
                    col_item.setForeground(2, QBrush(fk_color))
                    col_item.setForeground(3, QBrush(fk_color))
                else:
                    col_item.setForeground(0, QBrush(regular_color))

                table_item.addChild(col_item)

            # Expand table by default
            table_item.setExpanded(True)

        # Update statistics
        self._stats_label.setText(
            f"Tables: {table_count} | Columns: {column_count} | "
            f"Primary Keys: {pk_count} | Foreign Keys: {fk_count}"
        )

    def refresh(self):
        """Refresh the MLD display."""
        self.generate_mld()
