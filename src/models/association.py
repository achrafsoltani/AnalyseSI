from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .attribute import Attribute


@dataclass
class Association:
    """Represents an MCD association (relationship) with optional carrying attributes."""

    name: str
    attributes: List["Attribute"] = field(default_factory=list)  # Carrying attributes
    x: float = 0.0
    y: float = 0.0
    id: str = field(default_factory=lambda: str(uuid.uuid4()))

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "name": self.name,
            "attributes": [attr.to_dict() for attr in self.attributes],
            "x": self.x,
            "y": self.y
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Association":
        """Create an Association from a dictionary."""
        from .attribute import Attribute

        attributes = []
        for attr_data in data.get("attributes", []):
            if isinstance(attr_data, dict):
                attributes.append(Attribute.from_dict(attr_data))
            # Skip legacy string format

        return cls(
            id=data["id"],
            name=data["name"],
            attributes=attributes,
            x=data.get("x", 0.0),
            y=data.get("y", 0.0)
        )

    def add_attribute(self, attr: "Attribute") -> None:
        """Add a carrying attribute to this association."""
        self.attributes.append(attr)

    def remove_attribute(self, attr_name: str) -> None:
        """Remove a carrying attribute by name."""
        self.attributes = [a for a in self.attributes if a.name != attr_name]

    def has_attributes(self) -> bool:
        """Check if this association has carrying attributes."""
        return len(self.attributes) > 0

    def __str__(self) -> str:
        return f"Association({self.name})"
