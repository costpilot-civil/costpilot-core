from dataclasses import dataclass, field

from costpilot_core.models.material.attribute_definition import AttributeDefinition
from costpilot_core.models.material.keyword import MaterialKeyword


@dataclass(frozen=True)
class MaterialTemplate:
    material_type: str
    keywords: tuple[MaterialKeyword, ...] = field(default_factory=tuple)
    core_attributes: dict[str, AttributeDefinition] = field(default_factory=dict)
    supplementary_attributes: dict[str, AttributeDefinition] = field(
        default_factory=dict
    )

    def get_attribute(self, name: str) -> AttributeDefinition | None:
        attribute = self.core_attributes.get(name)
        if attribute is not None:
            return attribute

        return self.supplementary_attributes.get(name)
