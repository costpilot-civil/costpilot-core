from dataclasses import dataclass

from costpilot_core.models.commodity.commodity import Commodity
from costpilot_core.models.matching.match_status import MatchStatus


@dataclass
class MatchResult:
    status: MatchStatus
    commodity: Commodity | None
