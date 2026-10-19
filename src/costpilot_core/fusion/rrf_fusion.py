from collections import defaultdict

from costpilot_core.models.commodity.commodity import Commodity
from costpilot_core.models.matching.match_candidate import MatchCandidate


class RRFFusion:
    @staticmethod
    def fuse(
        candidate_lists: list[list[MatchCandidate]],
        top_k: int = 5,
        rrf_k: int = 60,
    ) -> list[MatchCandidate]:
        if top_k < 0:
            raise ValueError("top_k must be nonnegative.")
        if rrf_k < 0:
            raise ValueError("rrf_k must be nonnegative.")
        if top_k == 0:
            return []

        scores: dict[int, float] = defaultdict(float)
        commodities: dict[int, Commodity] = {}

        for candidates in candidate_lists:
            seen: set[int] = set()

            for rank, match_candidate in enumerate(candidates, start=1):
                commodity = match_candidate.commodity
                commodity_id = commodity.id

                if commodity_id in seen:
                    continue

                seen.add(commodity_id)

                scores[commodity_id] += 1.0 / (rrf_k + rank)
                commodities.setdefault(commodity_id, commodity)

        ranked_ids = sorted(
            scores,
            key=scores.__getitem__,
            reverse=True,
        )

        return [
            MatchCandidate(
                commodity=commodities[commodity_id],
                score=scores[commodity_id],
            )
            for commodity_id in ranked_ids[:top_k]
        ]
