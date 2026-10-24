import logging
import re
from decimal import Decimal, InvalidOperation
from typing import Any

from costpilot_core.models.material.attribute_definition import AttributeDefinition
from costpilot_core.models.material.extracted_material import ExtractedMaterial
from costpilot_core.models.material.material_template import MaterialTemplate

logger = logging.getLogger(__name__)


class AttributeExtractor:
    def extract(self, text: str, template: MaterialTemplate) -> ExtractedMaterial:
        return ExtractedMaterial(
            material_type=template.material_type,
            core_attributes=self._extract_attributes(text, template.core_attributes),
            supplementary_attributes=self._extract_attributes(
                text, template.supplementary_attributes
            ),
        )

    def _extract_attributes(
        self, text: str, attributes: dict[str, AttributeDefinition]
    ) -> dict[str, Any]:
        extracted: dict[str, Any] = {}
        for name, definition in attributes.items():
            value = self._extract_attribute(text, definition)
            if value is not None:
                extracted[name] = value
        return extracted

    def _extract_attribute(
        self, text: str, definition: AttributeDefinition
    ) -> Any | None:
        match definition.value_type:
            case "single":
                return self._extract_single(text, definition)
            case "multiple":
                return self._extract_multiple(text, definition)
            case "grouped":
                return self._extract_grouped(text, definition)
            case "numeric":
                return self._extract_numeric(text, definition)
            case _:
                raise ValueError(
                    f"Unsupported attribute type: {definition.value_type!r}"
                )

    @classmethod
    def _matches(cls, text: str, definition: AttributeDefinition) -> list[str]:
        matches: list[str] = []
        for value in definition.values:
            if not isinstance(value, str):
                continue
            spellings = (value, *definition.aliases.get(value, ()))
            if any(cls._contains_value(text, spelling) for spelling in spellings):
                matches.append(value)
        return matches

    @classmethod
    def _extract_single(
        cls, text: str, definition: AttributeDefinition
    ) -> str | None:
        matches = cls._matches(text, definition)
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            logger.warning(
                "Ambiguous single attribute | name=%s | matches=%s",
                definition.name, matches,
            )
        return None

    @classmethod
    def _extract_multiple(
        cls, text: str, definition: AttributeDefinition
    ) -> tuple[str, ...] | None:
        matches = cls._matches(text, definition)
        return tuple(matches) if matches else None

    @classmethod
    def _extract_grouped(
        cls, text: str, definition: AttributeDefinition
    ) -> dict[str, str] | None:
        result: dict[str, str] = {}
        for group_name, group in definition.groups.items():
            if not isinstance(group, dict):
                continue
            values = group.get("values", [])
            matches = [
                value for value in values
                if isinstance(value, str) and cls._contains_value(text, value)
            ]
            if len(matches) == 1:
                result[group_name] = matches[0]
            elif len(matches) > 1:
                logger.warning(
                    "Ambiguous grouped attribute | name=%s | group=%s | matches=%s",
                    definition.name, group_name, matches,
                )
        return result or None

    @staticmethod
    def _extract_numeric(
        text: str, definition: AttributeDefinition
    ) -> int | float | None:
        # Without an explicit context-bound pattern, extracting nothing is safer.
        if not definition.patterns:
            return None

        values: set[Decimal] = set()
        for pattern in definition.patterns:
            for match in re.finditer(pattern, text, flags=re.IGNORECASE):
                raw = match.group("value").replace(",", ".")
                try:
                    values.add(Decimal(raw))
                except InvalidOperation:
                    logger.warning(
                        "Invalid numeric attribute | name=%s | value=%s",
                        definition.name, raw,
                    )

        if len(values) != 1:
            if len(values) > 1:
                logger.warning(
                    "Ambiguous numeric attribute | name=%s | values=%s",
                    definition.name, sorted(values),
                )
            return None

        value = next(iter(values))
        if not value.is_finite():
            return None
        return int(value) if value == value.to_integral_value() else float(value)

    @staticmethod
    def _contains_value(text: str, value: str) -> bool:
        # Accept spaces in concrete grades without matching C8/10 inside LC8/10.
        concrete_grade = re.fullmatch(r"(LC|C)(\d+)/(\d+)", value, re.I)
        if concrete_grade:
            prefix, first, second = concrete_grade.groups()
            pattern = (
                rf"(?<!\w){prefix}\s*{first}\s*/\s*{second}(?!\w)"
            )
        elif re.fullmatch(r"SB[1-4]", value, re.I):
            pattern = rf"(?<!\w)SB\s*{re.escape(value[2:])}(?!\w)"
        else:
            pattern = rf"(?<!\w){re.escape(value)}(?!\w)"
        return re.search(pattern, text, flags=re.IGNORECASE) is not None
