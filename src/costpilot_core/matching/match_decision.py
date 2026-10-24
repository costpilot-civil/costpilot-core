"""Final matching decision from reranker relevance scores."""

from collections.abc import Sequence

from costpilot_core.models.matching.match_candidate import MatchCandidate
from costpilot_core.models.matching.match_result import MatchResult
from costpilot_core.models.matching.match_status import MatchStatus


def decide_match(
    *,
    ranked: Sequence[MatchCandidate],
    min_score: float,
    min_gap: float,
    structured: Sequence[MatchCandidate] = (),
) -> MatchResult:
    """Return AUTO_MATCHED, REVIEW_REQUIRED, or UNMATCHED.

    Input scores are normalized relevance scores in [0, 1], sorted descending.
    ``structured`` is retained for backwards compatibility; structured retrieval
    supplies candidates, but is not a mandatory condition for auto-matching.
    """
    if not 0 <= min_score <= 1:
        raise ValueError("min_score must be in [0, 1].")
    if not 0 <= min_gap <= 1:
        raise ValueError("min_gap must be in [0, 1].")

    if not ranked or ranked[0].score < min_score:
        return MatchResult(status=MatchStatus.UNMATCHED, commodity=None)

    best = ranked[0]
    has_competitor = len(ranked) > 1 and ranked[1].score >= min_score
    unique = not has_competitor or best.score - ranked[1].score >= min_gap

    return MatchResult(
        status=MatchStatus.AUTO_MATCHED if unique else MatchStatus.REVIEW_REQUIRED,
        commodity=best.commodity,
    )
