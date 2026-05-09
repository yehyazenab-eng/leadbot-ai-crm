from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class AIResult:
    reply: str
    confidence: float = 0.5


class AIProvider:
    def respond(self, message: str) -> AIResult:  # pragma: no cover
        raise NotImplementedError

