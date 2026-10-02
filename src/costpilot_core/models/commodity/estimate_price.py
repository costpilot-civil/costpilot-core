from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class EstimatePrice:
    id: int
    price_type: str
    price: Decimal
    currency: str

    factor: Decimal | None = None
    modified_date: date | None = None
    modified_user: str | None = None
    fixed_price: bool | None = None
