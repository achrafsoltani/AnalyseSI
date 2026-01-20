from typing import Dict, List, Optional
from .attribute import Attribute


class Dictionary:
    """Data dictionary managing all attributes."""

    def __init__(self):
        self._attributes: Dict[str, Attribute] = {}

    def add_attribute(self, attribute: Attribute) -> bool:
        """Add an attribute to the dictionary. Returns False if name already exists."""
        if attribute.name in self._attributes:
            return False
        self._attributes[attribute.name] = attribute
        return True

    def update_attribute(self, old_name: str, attribute: Attribute) -> bool:
        """Update an existing attribute. Handles name changes."""
        if old_name not in self._attributes:
            return False

        # If name changed, check for conflicts
        if old_name != attribute.name and attribute.name in self._attributes:
            return False

        # Remove old entry and add new one
        del self._attributes[old_name]
        self._attributes[attribute.name] = attribute
        return True

    def remove_attribute(self, name: str) -> bool:
        """Remove an attribute from the dictionary."""
        if name not in self._attributes:
            return False
        del self._attributes[name]
        return True

    def get_attribute(self, name: str) -> Optional[Attribute]:
        """Get an attribute by name."""
        return self._attributes.get(name)

    def get_all_attributes(self) -> List[Attribute]:
        """Get all attributes as a list."""
        return list(self._attributes.values())

    def get_attribute_names(self) -> List[str]:
        """Get all attribute names."""
        return list(self._attributes.keys())

    def has_attribute(self, name: str) -> bool:
        """Check if an attribute exists."""
        return name in self._attributes

    def clear(self) -> None:
        """Clear all attributes."""
        self._attributes.clear()

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "attributes": [attr.to_dict() for attr in self._attributes.values()]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Dictionary":
        """Create a Dictionary from a dictionary."""
        dictionary = cls()
        for attr_data in data.get("attributes", []):
            attr = Attribute.from_dict(attr_data)
            dictionary.add_attribute(attr)
        return dictionary

    def __len__(self) -> int:
        return len(self._attributes)

    def __iter__(self):
        return iter(self._attributes.values())
