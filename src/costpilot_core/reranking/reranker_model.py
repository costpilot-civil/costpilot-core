from abc import ABC, abstractmethod
from collections.abc import Sequence


class RerankerModel(ABC):
    """Interface for scoring query-document relevance."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Model identifier."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Model or configuration version."""

    @abstractmethod
    def score(
        self,
        query: str,
        document: str,
    ) -> float:
        """Score a single query-document pair."""

    @abstractmethod
    def score_batch(
        self,
        query: str,
        documents: Sequence[str],
    ) -> list[float]:
        """Score documents in input order."""
