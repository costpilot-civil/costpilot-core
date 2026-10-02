from enum import StrEnum


class MatchStatus(StrEnum):
    AUTO_MATCHED = "auto_matched"
    REVIEW_REQUIRED = "review_required"
    UNMATCHED = "unmatched"
