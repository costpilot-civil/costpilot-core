from costpilot_core.models.commodity.commodity import Commodity
from costpilot_core.models.tender.tender_item import TenderItem


class TextBuilder:
    @staticmethod
    def build_tender_item_text(item: TenderItem) -> str:
        parts = [
            item.short_text,
            item.long_text,
            item.unit,
        ]

        return " ".join(
            part.strip() for part in parts if part is not None and part.strip()
        )

    @staticmethod
    def build_commodity_text(commodity: Commodity) -> str:
        parts = [
            commodity.code,
            commodity.description,
            commodity.unit,
            commodity.category_path,
        ]

        return " ".join(
            part.strip() for part in parts if part is not None and part.strip()
        )
