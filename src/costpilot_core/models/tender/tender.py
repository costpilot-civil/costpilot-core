from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass(slots=True)
class TenderItem:
    oz: str
    number_part: str
    short_text: str
    long_text: str
    quantity: Decimal | None
    unit: str | None


@dataclass(slots=True)
class TenderCategory:
    oz: str
    number_part: str
    name: str
    children: list[TenderCategory | TenderItem] = field(default_factory=list)


@dataclass(slots=True)
class ParsedTender:
    nodes: list[TenderCategory | TenderItem] = field(default_factory=list)
