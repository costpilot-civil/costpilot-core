from costpilot_core.material.attribute_extractor import AttributeExtractor
from costpilot_core.material.classifier import MaterialClassifier
from costpilot_core.material.registry import MaterialRegistry
from costpilot_core.models.material.extracted_material import ExtractedMaterial


class MaterialExtractor:
    def __init__(
        self,
        registry: MaterialRegistry,
        classifier: MaterialClassifier,
        attribute_extractor: AttributeExtractor,
    ) -> None:
        self._registry = registry
        self._classifier = classifier
        self._attribute_extractor = attribute_extractor

    def extract(self, text: str) -> ExtractedMaterial | None:
        material_type = self._classifier.classify(text)

        if material_type is None:
            return None

        template = self._registry.get(material_type)

        return self._attribute_extractor.extract(
            text=text,
            template=template,
        )
