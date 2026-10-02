from dataclasses import dataclass, field

from costpilot_core.models.commodity.commodity_price import CommodityPrice
from costpilot_core.models.commodity.estimate_price import EstimatePrice


@dataclass
class Commodity:
    id: int
    code: str
    description: str | None
    unit: str | None
    category_path: str

    commodity_prices: list[CommodityPrice] = field(default_factory=list)
    estimate_prices: list[EstimatePrice] = field(default_factory=list)
