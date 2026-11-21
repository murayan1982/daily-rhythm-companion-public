from collections.abc import Callable, Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from hashlib import sha256
from threading import Lock
from typing import Literal, Protocol

from app.models.advice import AdviceCharacterId, AdviceMood


QuotaExceeded = Literal["user_quota_exceeded", "global_quota_exceeded"]


class AdviceQuota(Protocol):
    def reserve(self, user_id: str) -> QuotaExceeded | None:
        """Atomically charge both budgets, or return the exceeded limit without charging."""
        ...


class AdviceGenerator(Protocol):
    def __call__(self, *, mood: AdviceMood, character_id: AdviceCharacterId) -> str:
        """Perform at most one upstream call per reservation, without logging text."""
        ...


@dataclass(frozen=True)
class PublicAdviceRuntime:
    authenticate: Callable[[str], str | None]
    quota: AdviceQuota
    generate: AdviceGenerator


class LocalAdviceTokenVerifier:
    """Local verification only, with separately issued tokens mapped to server-side IDs."""

    def __init__(self, tokens: Mapping[str, str]):
        self._identities = {
            sha256(token.encode()).digest(): user_id
            for token, user_id in tokens.items()
        }

    def __call__(self, token: str) -> str | None:
        return self._identities.get(sha256(token.encode()).digest())


class InMemoryDailyAdviceQuota:
    """Single-process test quotas, reset at UTC midnight or on restart."""

    def __init__(self, *, per_user: int, total: int):
        if per_user <= 0 or total <= 0:
            raise ValueError("Test quotas must be positive.")
        self._per_user_limit = per_user
        self._total_limit = total
        self._lock = Lock()
        self._day = datetime.now(UTC).date()
        self._by_user: dict[str, int] = {}
        self._total = 0

    def reserve(self, user_id: str) -> QuotaExceeded | None:
        with self._lock:
            today = datetime.now(UTC).date()
            if today > self._day:
                self._day = today
                self._by_user.clear()
                self._total = 0
            used = self._by_user.get(user_id, 0)
            if used >= self._per_user_limit:
                return "user_quota_exceeded"
            if self._total >= self._total_limit:
                return "global_quota_exceeded"

            # Charge when admitted. Upstream errors do not refund a generation attempt.
            self._by_user[user_id] = used + 1
            self._total += 1
            return None
