from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
import uuid

if TYPE_CHECKING:
    from .attribute import Attribute


@dataclass
class Entity:
    """Represents an MCD entity with its own attributes."""

    name: str
    attributes: List["Attribute"] = field(default_factory=list)
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
    def from_dict(cls, data: dict) -> "Entity":
        """Create an Entity from a dictionary."""
        from .attribute import Attribute

        attributes = []
        for attr_data in data.get("attributes", []):
            if isinstance(attr_data, dict):
                attributes.append(Attribute.from_dict(attr_data))
            else:
                # Legacy format: just attribute names (skip)
                pass

        return cls(
            id=data["id"],
            name=data["name"],
            attributes=attributes,
            x=data.get("x", 0.0),
            y=data.get("y", 0.0)
        )

    def add_attribute(self, attr: "Attribute") -> None:
        """Add an attribute to this entity."""
        self.attributes.append(attr)

    def remove_attribute(self, attr_name: str) -> None:
        """Remove an attribute by name."""
        self.attributes = [a for a in self.attributes if a.name != attr_name]

    def get_attribute(self, name: str) -> "Attribute | None":
        """Get an attribute by name."""
        for attr in self.attributes:
            if attr.name == name:
                return attr
        return None

    def get_primary_keys(self) -> List["Attribute"]:
        """Get list of primary key attributes."""
        return [attr for attr in self.attributes if attr.is_primary_key]

    def get_primary_key_names(self) -> List[str]:
        """Get list of primary key attribute names."""
        return [attr.name for attr in self.attributes if attr.is_primary_key]

    def __str__(self) -> str:
        return f"Entity({self.name})"
