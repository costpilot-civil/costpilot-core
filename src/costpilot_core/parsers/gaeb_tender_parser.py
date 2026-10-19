import re
from decimal import Decimal, InvalidOperation
from pathlib import Path
from xml.etree.ElementTree import Element

from defusedxml import ElementTree as ET

from costpilot_core.models.tender.tender import ParsedTender, TenderCategory, TenderItem


class GAEBTenderParser:
    def parse(self, file_path: str | Path) -> ParsedTender:
        root = ET.parse(file_path).getroot()
        if root is None:
            raise ValueError("GAEB XML root element not found.")

        namespace = self._get_namespace(root)

        award = root.find(self._tag("Award", namespace))
        if award is None:
            raise ValueError("GAEB Award element not found.")

        boq = award.find(self._tag("BoQ", namespace))
        if boq is None:
            raise ValueError("GAEB BoQ element not found.")

        boq_info = boq.find(self._tag("BoQInfo", namespace))
        if boq_info is None:
            raise ValueError("GAEB BoQInfo element not found.")

        category_lengths, item_length = self._read_oz_structure(boq_info, namespace)

        boq_body = boq.find(self._tag("BoQBody", namespace))
        if boq_body is None:
            raise ValueError("GAEB BoQBody element not found.")

        nodes = self._parse_body(
            body=boq_body,
            namespace=namespace,
            category_parts=[],
            category_lengths=category_lengths,
            item_length=item_length,
        )

        return ParsedTender(nodes=nodes)

    @staticmethod
    def _get_namespace(root: Element) -> str:
        if root.tag.startswith("{"):
            return root.tag.split("}", 1)[0][1:]
        return ""

    @staticmethod
    def _tag(name: str, namespace: str) -> str:
        if namespace:
            return f"{{{namespace}}}{name}"
        return name

    @classmethod
    def _read_oz_structure(
        cls,
        boq_info: Element,
        namespace: str,
    ) -> tuple[list[int], int]:
        category_lengths: list[int] = []
        item_length = 0

        for breakdown in boq_info.findall(cls._tag("BoQBkdn", namespace)):
            breakdown_type = breakdown.findtext(cls._tag("Type", namespace))
            length_text = breakdown.findtext(cls._tag("Length", namespace))

            if length_text is None:
                continue

            length = int(length_text)

            if breakdown_type == "BoQLevel":
                category_lengths.append(length)
            elif breakdown_type == "Item":
                item_length = length

        return category_lengths, item_length

    @classmethod
    def _parse_body(
        cls,
        *,
        body: Element,
        namespace: str,
        category_parts: list[str],
        category_lengths: list[int],
        item_length: int,
    ) -> list[TenderCategory | TenderItem]:
        nodes: list[TenderCategory | TenderItem] = []

        for element in body:
            if element.tag == cls._tag("BoQCtgy", namespace):
                number_part = element.get("RNoPart")
                if not number_part:
                    raise ValueError("Category RNoPart is missing.")

                current_parts = [*category_parts, number_part]

                category_body = element.find(cls._tag("BoQBody", namespace))

                children = (
                    cls._parse_body(
                        body=category_body,
                        namespace=namespace,
                        category_parts=current_parts,
                        category_lengths=category_lengths,
                        item_length=item_length,
                    )
                    if category_body is not None
                    else []
                )

                nodes.append(
                    TenderCategory(
                        oz=cls._build_oz(
                            current_parts,
                            category_lengths,
                        ),
                        number_part=number_part,
                        name=cls._read_category_name(element, namespace),
                        children=children,
                    )
                )

            elif element.tag == cls._tag("Itemlist", namespace):
                for item in element.findall(cls._tag("Item", namespace)):
                    nodes.append(
                        cls._parse_item(
                            item=item,
                            namespace=namespace,
                            category_parts=category_parts,
                            category_lengths=category_lengths,
                            item_length=item_length,
                        )
                    )

            elif element.tag == cls._tag("Item", namespace):
                nodes.append(
                    cls._parse_item(
                        item=element,
                        namespace=namespace,
                        category_parts=category_parts,
                        category_lengths=category_lengths,
                        item_length=item_length,
                    )
                )

        return nodes

    @classmethod
    def _read_category_name(
        cls,
        category: Element,
        namespace: str,
    ) -> str:
        paths = (
            ("BoQCatInfo", "LblTx"),
            ("BoQCatInfo", "Label"),
            ("LblTx",),
        )

        for path in paths:
            qualified_path = "/".join(cls._tag(part, namespace) for part in path)

            element = category.find(qualified_path)
            text = cls._clean_text(element)

            if text:
                return text

        return ""

    @classmethod
    def _parse_item(
        cls,
        *,
        item: Element,
        namespace: str,
        category_parts: list[str],
        category_lengths: list[int],
        item_length: int,
    ) -> TenderItem:
        number_part = item.get("RNoPart")
        if not number_part:
            raise ValueError("Item RNoPart is missing.")

        oz = cls._build_oz(
            [*category_parts, number_part],
            [*category_lengths, item_length],
        )

        quantity_text = item.findtext(cls._tag("Qty", namespace))

        quantity: Decimal | None = None

        if quantity_text is not None and quantity_text.strip():
            try:
                quantity = Decimal(quantity_text.strip())
            except InvalidOperation as exc:
                raise ValueError(f"Invalid quantity for item {oz}.") from exc

            if not quantity.is_finite() or quantity < 0:
                raise ValueError(f"Invalid quantity for item {oz}.")

        unit = item.findtext(cls._tag("QU", namespace))

        text_base = (
            cls._tag("Description", namespace)
            + "/"
            + cls._tag("CompleteText", namespace)
        )

        short_text_element = item.find(
            text_base + "/" + cls._tag("OutlineText", namespace)
        )

        long_text_element = item.find(
            text_base + "/" + cls._tag("DetailTxt", namespace)
        )

        return TenderItem(
            oz=oz,
            number_part=number_part,
            short_text=cls._clean_text(short_text_element),
            long_text=cls._clean_text(long_text_element),
            quantity=quantity,
            unit=unit.strip() if unit else None,
        )

    @staticmethod
    def _build_oz(
        parts: list[str],
        lengths: list[int],
    ) -> str:
        return ".".join(
            part.zfill(lengths[index]) if index < len(lengths) else part
            for index, part in enumerate(parts)
        )

    @staticmethod
    def _clean_text(element: Element | None) -> str:
        if element is None:
            return ""

        text = " ".join(part.strip() for part in element.itertext() if part.strip())

        return re.sub(r"\s+", " ", text).strip()
