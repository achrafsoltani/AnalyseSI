from typing import List
from ..models.project import Project
from ..models.mld import MLDTable, MLDColumn


class MLDTransformer:
    """Transforms MCD (Conceptual Data Model) to MLD (Logical Data Model)."""

    def __init__(self, project: Project):
        self._project = project

    def transform(self) -> List[MLDTable]:
        """Transform the MCD to a list of MLD tables."""
        tables = []

        # Transform entities to tables
        for entity in self._project.get_all_entities():
            table = self._transform_entity(entity)
            tables.append(table)

        # Transform N-N associations to junction tables
        for assoc in self._project.get_all_associations():
            table = self._transform_association(assoc)
            if table:
                tables.append(table)

        # Add foreign keys for 1-N relationships
        self._add_foreign_keys(tables)

        return tables

    def _transform_entity(self, entity) -> MLDTable:
        """Transform an entity to an MLD table."""
        table = MLDTable(
            name=self._safe_name(entity.name),
            source_type="entity",
            source_id=entity.id
        )

        # Add columns from entity attributes
        for attr in entity.attributes:
            column = MLDColumn(
                name=self._safe_name(attr.name),
                data_type=attr.get_sql_type(),
                is_primary_key=attr.is_primary_key,
                is_nullable=not attr.is_primary_key
            )
            table.columns.append(column)

        return table

    def _transform_association(self, assoc) -> MLDTable | None:
        """Transform an association to a junction table if needed."""
        links = self._project.get_links_for_association(assoc.id)

        if len(links) < 2:
            return None

        # Check if this is an N-N relationship or has carrying attributes
        n_links = [link for link in links if link.cardinality_max == "N"]

        if len(n_links) >= 2 or assoc.has_attributes():
            return self._create_junction_table(assoc, links)

        return None

    def _create_junction_table(self, assoc, links) -> MLDTable:
        """Create a junction table for N-N relationships."""
        table = MLDTable(
            name=self._safe_name(assoc.name),
            source_type="association",
            source_id=assoc.id
        )

        # Add foreign key columns for each linked entity
        for link in links:
            entity = self._project.get_entity(link.entity_id)
            if entity:
                for pk_attr in entity.get_primary_keys():
                    col_name = f"fk_{self._safe_name(entity.name)}_{pk_attr.name}"
                    column = MLDColumn(
                        name=col_name,
                        data_type=pk_attr.get_sql_type(),
                        is_primary_key=True,
                        is_foreign_key=True,
                        references_table=self._safe_name(entity.name),
                        references_column=self._safe_name(pk_attr.name),
                        is_nullable=False
                    )
                    table.columns.append(column)

        # Add carrying attributes
        for attr in assoc.attributes:
            column = MLDColumn(
                name=self._safe_name(attr.name),
                data_type=attr.get_sql_type(),
                is_primary_key=False,
                is_nullable=True
            )
            table.columns.append(column)

        return table

    def _add_foreign_keys(self, tables: List[MLDTable]):
        """Add foreign key columns for 1-N relationships."""
        # Build a lookup for entity tables by source_id
        entity_tables = {t.source_id: t for t in tables if t.source_type == "entity"}

        for entity in self._project.get_all_entities():
            links = self._project.get_links_for_entity(entity.id)

            for link in links:
                if link.cardinality_max == "1":  # This entity is on the "1" side
                    # Get other links in the same association
                    assoc_links = self._project.get_links_for_association(link.association_id)

                    for other_link in assoc_links:
                        if other_link.entity_id != entity.id and other_link.cardinality_max == "N":
                            # N-1 relationship: add FK to this entity's table
                            other_entity = self._project.get_entity(other_link.entity_id)
                            if other_entity and entity.id in entity_tables:
                                table = entity_tables[entity.id]
                                for pk_attr in other_entity.get_primary_keys():
                                    col_name = f"fk_{self._safe_name(other_entity.name)}_{pk_attr.name}"
                                    # Check if column already exists
                                    if not any(c.name == col_name for c in table.columns):
                                        column = MLDColumn(
                                            name=col_name,
                                            data_type=pk_attr.get_sql_type(),
                                            is_primary_key=False,
                                            is_foreign_key=True,
                                            references_table=self._safe_name(other_entity.name),
                                            references_column=self._safe_name(pk_attr.name),
                                            is_nullable=link.cardinality_min == "0"
                                        )
                                        table.columns.append(column)

    def _safe_name(self, name: str) -> str:
        """Convert name to safe SQL identifier."""
        safe = name.lower().replace(" ", "_").replace("-", "_")
        safe = "".join(c for c in safe if c.isalnum() or c == "_")
        return safe
