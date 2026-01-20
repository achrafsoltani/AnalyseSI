from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Attribute:
    """Represents a data dictionary attribute."""

    name: str
    data_type: str  # VARCHAR, INT, DATE, etc.
    size: Optional[int] = None
    is_primary_key: bool = False

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "name": self.name,
            "type": self.data_type,
            "size": self.size,
            "pk": self.is_primary_key
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Attribute":
        """Create an Attribute from a dictionary."""
        return cls(
            name=data["name"],
            data_type=data["type"],
            size=data.get("size"),
            is_primary_key=data.get("pk", False)
        )

    def get_sql_type(self) -> str:
        """Get the SQL type declaration."""
        if self.size is not None and self.data_type in ("VARCHAR", "CHAR", "DECIMAL"):
            return f"{self.data_type}({self.size})"
        return self.data_type

    def __str__(self) -> str:
        pk_marker = " [PK]" if self.is_primary_key else ""
        return f"{self.name}: {self.get_sql_type()}{pk_marker}"
