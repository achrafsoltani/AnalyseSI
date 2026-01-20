from dataclasses import dataclass, field
from typing import List
import uuid


@dataclass
class Entity:
    """Represents an MCD entity."""

    name: str
    attributes: List[str] = field(default_factory=list)  # References to dictionary attribute names
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
    def from_dict(cls, data: dict) -> "Entity":
        """Create an Entity from a dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            attributes=data.get("attributes", []),
            x=data.get("x", 0.0),
            y=data.get("y", 0.0)
        )

    def add_attribute(self, attr_name: str) -> None:
        """Add an attribute reference to this entity."""
        if attr_name not in self.attributes:
            self.attributes.append(attr_name)

    def remove_attribute(self, attr_name: str) -> None:
        """Remove an attribute reference from this entity."""
        if attr_name in self.attributes:
            self.attributes.remove(attr_name)

    def get_primary_keys(self, dictionary: "Dictionary") -> List[str]:
        """Get list of primary key attribute names."""
        pks = []
        for attr_name in self.attributes:
            attr = dictionary.get_attribute(attr_name)
            if attr and attr.is_primary_key:
                pks.append(attr_name)
        return pks

    def __str__(self) -> str:
        return f"Entity({self.name})"
