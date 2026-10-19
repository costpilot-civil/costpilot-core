from abc import ABC, abstractmethod
from collections.abc import Sequence


class EmbeddingModel(ABC):
    """Interface for encoding text into dense vectors."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Model identifier."""

    @property
    @abstractmethod
    def version(self) -> str:
        """Model or configuration version."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        """Output vector dimension."""

    @abstractmethod
    def encode(self, text: str) -> list[float]:
        """Encode a single text."""

    @abstractmethod
    def encode_batch(
        self,
        texts: Sequence[str],
    ) -> list[list[float]]:
        """Encode multiple texts in input order."""
