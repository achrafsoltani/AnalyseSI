from ..models.project import Project


class MCDController:
    """Controller for MCD operations."""

    def __init__(self, project: Project):
        self._project = project

    def validate(self) -> list[str]:
        """Validate the MCD model and return list of errors/warnings."""
        errors = []

        # Check for entities
        entities = self._project.get_all_entities()
        if not entities:
            errors.append("No entities defined. Add at least one entity.")

        # Check entities have at least one primary key
        for entity in entities:
            has_pk = any(attr.is_primary_key for attr in entity.attributes)
            if not has_pk:
                errors.append(f"Entity '{entity.name}' has no primary key attribute.")

        # Check associations have at least 2 links
        for assoc in self._project.get_all_associations():
            links = self._project.get_links_for_association(assoc.id)
            if len(links) < 2:
                errors.append(
                    f"Association '{assoc.name}' must be connected to at least 2 entities."
                )

        # Check for orphan entities (no links)
        for entity in self._project.get_all_entities():
            links = self._project.get_links_for_entity(entity.id)
            if len(links) == 0:
                errors.append(f"Entity '{entity.name}' is not connected to any association.")

        return errors

    def get_statistics(self) -> dict:
        """Get statistics about the current model."""
        # Count all attributes across all entities
        total_attributes = sum(
            len(entity.attributes) for entity in self._project.get_all_entities()
        )
        return {
            "attributes": total_attributes,
            "entities": len(self._project.get_all_entities()),
            "associations": len(self._project.get_all_associations()),
            "links": len(self._project.get_all_links())
        }
