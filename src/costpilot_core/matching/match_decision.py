from collections.abc import Sequence

from costpilot_core.models.matching.match_candidate import MatchCandidate
from costpilot_core.models.matching.match_result import MatchResult
from costpilot_core.models.matching.match_status import MatchStatus


def decide_match(
    *,
    ranked: Sequence[MatchCandidate],
    structured: Sequence[MatchCandidate],
    min_score: float,
    min_gap: float,
) -> MatchResult:
    if not ranked:
        return MatchResult(
            status=MatchStatus.UNMATCHED,
            commodity=None,
        )

    best = ranked[0]

    # 1. Minimum reranker score
    score_matches = best.score >= min_score

    # 2. Score gap between Top 1 and Top 2
    gap_matches = len(ranked) >= 2 and best.score - ranked[1].score >= min_gap

    # 3. Structured retrieval confirmation
    structured_matches = any(
        candidate.commodity.id == best.commodity.id for candidate in structured
    )

    # 4. Final decision
    if score_matches and gap_matches and structured_matches:
        return MatchResult(
            status=MatchStatus.AUTO_MATCHED,
            commodity=best.commodity,
        )

    return MatchResult(
        status=MatchStatus.REVIEW_REQUIRED,
        commodity=best.commodity,
    )
