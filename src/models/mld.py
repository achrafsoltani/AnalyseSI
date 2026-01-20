from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MLDColumn:
    """Represents a column in a logical table."""
    name: str
    data_type: str
    is_primary_key: bool = False
    is_foreign_key: bool = False
    references_table: Optional[str] = None
    references_column: Optional[str] = None
    is_nullable: bool = True


@dataclass
class MLDTable:
    """Represents a table in the logical data model."""
    name: str
    columns: List[MLDColumn] = field(default_factory=list)
    source_type: str = "entity"  # "entity" or "association"
    source_id: Optional[str] = None

    def get_primary_keys(self) -> List[MLDColumn]:
        """Get all primary key columns."""
        return [col for col in self.columns if col.is_primary_key]

    def get_foreign_keys(self) -> List[MLDColumn]:
        """Get all foreign key columns."""
        return [col for col in self.columns if col.is_foreign_key]
