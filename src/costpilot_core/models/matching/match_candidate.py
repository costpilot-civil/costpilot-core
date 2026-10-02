from dataclasses import dataclass

from costpilot_core.models.commodity.commodity import Commodity


@dataclass
class MatchCandidate:
    commodity: Commodity
    score: float
