from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class Association:
    """Represents an MCD association (relationship)."""

    name: str
    attributes: List[str] = field(default_factory=list)  # Carrying attributes (optional)
    x: float = 0.0
    y: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "attributes": self.attributes,
            "x": self.x,
            "y": self.y
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Association":
        """Create an Association from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            attributes=data.get("attributes", []),
            x=data.get("x", 0.0),
            y=data.get("y", 0.0)
        )

    def add_attribute(self, attr_name: str) -> None:
        """Add a carrying attribute to this association."""
        if attr_name not in self.attributes:
            self.attributes.append(attr_name)

    def remove_attribute(self, attr_name: str) -> None:
        """Remove a carrying attribute from this association."""
        if attr_name in self.attributes:
            self.attributes.remove(attr_name)

    def has_attributes(self) -> bool:
        """Check if this association has carrying attributes."""
        return len(self.attributes) > 0

    def __str__(self) -> str:
        return f"Association({self.name})"
