from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QPushButton, QMessageBox, QFileDialog
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QTextCharFormat, QColor, QSyntaxHighlighter

from ..models.project import Project
from ..controllers.sql_generator import SQLGenerator


class SQLHighlighter(QSyntaxHighlighter):
    """Simple SQL syntax highlighter."""

    KEYWORDS = [
        "CREATE", "TABLE", "PRIMARY", "KEY", "FOREIGN", "REFERENCES",
        "NOT", "NULL", "UNIQUE", "INDEX", "ALTER", "DROP", "INSERT",
        "INTO", "VALUES", "SELECT", "FROM", "WHERE", "AND", "OR",
        "INT", "INTEGER", "BIGINT", "SMALLINT", "VARCHAR", "CHAR",
        "TEXT", "BOOLEAN", "DATE", "TIME", "TIMESTAMP", "DECIMAL",
        "FLOAT", "DOUBLE", "SERIAL"
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self._keyword_format = QTextCharFormat()
        self._keyword_format.setForeground(QColor("#0000FF"))
        self._keyword_format.setFontWeight(QFont.Bold)

        self._comment_format = QTextCharFormat()
        self._comment_format.setForeground(QColor("#008000"))
        self._comment_format.setFontItalic(True)

        self._string_format = QTextCharFormat()
        self._string_format.setForeground(QColor("#A31515"))

    def highlightBlock(self, text: str):
        # Highlight keywords
        for keyword in self.KEYWORDS:
            index = 0
            while True:
                # Case-insensitive search
                text_upper = text.upper()
                idx = text_upper.find(keyword, index)
                if idx == -1:
                    break
                # Check it's a whole word
                before_ok = idx == 0 or not text[idx - 1].isalnum()
                after_ok = (idx + len(keyword) >= len(text) or
                           not text[idx + len(keyword)].isalnum())
                if before_ok and after_ok:
                    self.setFormat(idx, len(keyword), self._keyword_format)
                index = idx + len(keyword)

        # Highlight comments (-- style)
        idx = text.find("--")
        if idx >= 0:
            self.setFormat(idx, len(text) - idx, self._comment_format)

        # Highlight strings
        in_string = False
        start = 0
        for i, char in enumerate(text):
            if char == "'":
                if not in_string:
                    in_string = True
                    start = i
                else:
                    self.setFormat(start, i - start + 1, self._string_format)
                    in_string = False


class SQLView(QWidget):
    """View for displaying and exporting generated SQL."""

    def __init__(self, project: Project, parent=None):
        super().__init__(parent)
        self._project = project
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # Toolbar
        toolbar = QHBoxLayout()

        self._generate_btn = QPushButton("Generate SQL")
        self._generate_btn.clicked.connect(self.generate_sql)
        toolbar.addWidget(self._generate_btn)

        self._copy_btn = QPushButton("Copy to Clipboard")
        self._copy_btn.clicked.connect(self._copy_to_clipboard)
        toolbar.addWidget(self._copy_btn)

        self._export_btn = QPushButton("Export to File")
        self._export_btn.clicked.connect(self._export_to_file)
        toolbar.addWidget(self._export_btn)

        toolbar.addStretch()
        layout.addLayout(toolbar)

        # SQL text editor
        self._text_edit = QTextEdit()
        self._text_edit.setReadOnly(True)
        font = QFont("Monospace")
        font.setStyleHint(QFont.Monospace)
        font.setPointSize(10)
        self._text_edit.setFont(font)

        # Add syntax highlighter
        self._highlighter = SQLHighlighter(self._text_edit.document())

        layout.addWidget(self._text_edit)

    def set_project(self, project: Project):
        """Set a new project."""
        self._project = project
        self._text_edit.clear()

    def generate_sql(self):
        """Generate SQL from the current project."""
        generator = SQLGenerator(self._project)
        sql = generator.generate()
        self._text_edit.setPlainText(sql)

    def _copy_to_clipboard(self):
        """Copy SQL to clipboard."""
        from PySide6.QtWidgets import QApplication
        text = self._text_edit.toPlainText()
        if text:
            QApplication.clipboard().setText(text)
            QMessageBox.information(self, "Copied", "SQL copied to clipboard.")
        else:
            QMessageBox.warning(self, "Empty", "No SQL to copy. Generate SQL first.")

    def _export_to_file(self):
        """Export SQL to a file."""
        text = self._text_edit.toPlainText()
        if not text:
            QMessageBox.warning(self, "Empty", "No SQL to export. Generate SQL first.")
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export SQL",
            "schema.sql",
            "SQL Files (*.sql);;All Files (*)"
        )

        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(text)
                QMessageBox.information(
                    self, "Exported",
                    f"SQL exported to:\n{file_path}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self, "Error",
                    f"Failed to export SQL:\n{str(e)}"
                )
