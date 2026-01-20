from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout,
    QLineEdit, QTextEdit, QDialogButtonBox, QLabel
)
from PySide6.QtCore import Qt

from ...models.project import Project


class ProjectPropertiesDialog(QDialog):
    """Dialog for editing project properties/metadata."""

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self._project = project
        self._setup_ui()
        self._load_data()

    def _setup_ui(self):
        self.setWindowTitle("Project Properties")
        self.setMinimumSize(450, 350)

        layout = QVBoxLayout(self)

        form = QFormLayout()

        # Project name
        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("e.g., Customer Database, Inventory System")
        form.addRow("Project Name:", self._name_edit)

        # Author
        self._author_edit = QLineEdit()
        self._author_edit.setPlaceholderText("e.g., John Doe")
        form.addRow("Author:", self._author_edit)

        # Description
        self._description_edit = QTextEdit()
        self._description_edit.setPlaceholderText("Enter a description of the project...")
        self._description_edit.setMaximumHeight(100)
        form.addRow("Description:", self._description_edit)

        layout.addLayout(form)

        # Metadata info (read-only)
        layout.addSpacing(10)
        layout.addWidget(QLabel("Metadata:"))

        self._created_label = QLabel()
        self._created_label.setStyleSheet("color: gray;")
        layout.addWidget(self._created_label)

        self._modified_label = QLabel()
        self._modified_label.setStyleSheet("color: gray;")
        layout.addWidget(self._modified_label)

        layout.addStretch()

        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _load_data(self):
        """Load data from the project."""
        self._name_edit.setText(self._project.name)
        self._author_edit.setText(self._project.author)
        self._description_edit.setPlainText(self._project.description)

        # Format timestamps
        created = self._format_timestamp(self._project.created_at)
        modified = self._format_timestamp(self._project.modified_at)

        self._created_label.setText(f"Created: {created}")
        self._modified_label.setText(f"Last modified: {modified}")

    def _format_timestamp(self, iso_timestamp: str) -> str:
        """Format ISO timestamp to human-readable format."""
        try:
            from datetime import datetime
            dt = datetime.fromisoformat(iso_timestamp)
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, TypeError):
            return iso_timestamp or "Unknown"

    def _on_accept(self):
        """Validate and accept the dialog."""
        name = self._name_edit.text().strip()
        if not name:
            self._name_edit.setFocus()
            return

        self.accept()

    def apply_to_project(self):
        """Apply the dialog values to the project."""
        self._project.name = self._name_edit.text().strip()
        self._project.author = self._author_edit.text().strip()
        self._project.description = self._description_edit.toPlainText().strip()
