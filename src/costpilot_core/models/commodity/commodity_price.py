from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class CommodityPrice:
    id: int
    unit_price: Decimal
    currency: str

    discount: Decimal | None = None
    freight_costs: Decimal | None = None
    miscellaneous: Decimal | None = None
    wastage: Decimal | None = None

    modified_date: date | None = None
    modified_user: str | None = None
