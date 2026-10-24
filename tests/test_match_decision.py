from costpilot_core.matching.match_decision import decide_match
from costpilot_core.models.commodity.commodity import Commodity
from costpilot_core.models.matching.match_candidate import MatchCandidate
from costpilot_core.models.matching.match_status import MatchStatus


def ranked(*scores: float) -> list[MatchCandidate]:
    return [
        MatchCandidate(
            commodity=Commodity(
                id=i + 1,
                code=f"C-{i + 1}",
                description="",
                unit="m3",
                category_path="Concrete",
            ),
            score=score,
        )
        for i, score in enumerate(scores)
    ]


def test_empty_unmatched():
    decision = decide_match(ranked=[], min_score=0.6, min_gap=0.1)
    assert decision.status == MatchStatus.UNMATCHED
    assert decision.commodity is None


def test_low_score_unmatched():
    decision = decide_match(ranked=ranked(0.59, 0.40), min_score=0.6, min_gap=0.1)
    assert decision.status == MatchStatus.UNMATCHED
    assert decision.commodity is None


def test_unique_single_candidate_auto():
    decision = decide_match(ranked=ranked(0.8), min_score=0.6, min_gap=0.1)
    assert decision.status == MatchStatus.AUTO_MATCHED
    assert decision.commodity.id == 1  # type: ignore


def test_unique_strong_gap_auto_without_structured():
    decision = decide_match(
        ranked=ranked(0.86, 0.70, 0.69), structured=[], min_score=0.6, min_gap=0.1
    )
    assert decision.status == MatchStatus.AUTO_MATCHED
    assert decision.commodity.id == 1  # type: ignore


def test_only_one_above_cutoff_auto():
    decision = decide_match(ranked=ranked(0.8, 0.5), min_score=0.6, min_gap=0.1)
    assert decision.status == MatchStatus.AUTO_MATCHED


def test_close_scores_review():
    decision = decide_match(ranked=ranked(0.86, 0.82, 0.8), min_score=0.6, min_gap=0.1)
    assert decision.status == MatchStatus.REVIEW_REQUIRED
    assert decision.commodity.id == 1  # type: ignore


def test_invalid_thresholds_raise():
    import pytest

    with pytest.raises(ValueError):
        decide_match(ranked=ranked(0.9), min_score=1.1, min_gap=0.1)
