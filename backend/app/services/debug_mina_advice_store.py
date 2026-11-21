from collections import OrderedDict
from secrets import token_urlsafe
from threading import Lock
from time import monotonic
from typing import Callable


class DebugMinaAdviceStore:
    """Bounded process-local references to validated Mina advice."""

    def __init__(self, *, clock: Callable[[], float] = monotonic) -> None:
        self._clock = clock
        self._entries: OrderedDict[str, tuple[float, str]] = OrderedDict()
        self._lock = Lock()

    def issue(self, message: str) -> str:
        with self._lock:
            now = self._clock()
            while self._entries:
                expires, _ = next(iter(self._entries.values()))
                if expires > now and len(self._entries) < 128:
                    break
                self._entries.popitem(last=False)
            ref = token_urlsafe(24)
            self._entries[ref] = (now + 300, message)
            return ref

    def resolve(self, ref: str) -> str | None:
        with self._lock:
            entry = self._entries.get(ref)
            if entry is None:
                return None
            expires, message = entry
            if expires <= self._clock():
                del self._entries[ref]
                return None
            return message
