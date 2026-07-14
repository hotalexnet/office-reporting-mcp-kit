"""Transport replay guard skeleton."""

from __future__ import annotations

from dataclasses import dataclass
from time import time


@dataclass(frozen=True)
class ReplayCheck:
    request_nonce: str | None
    request_timestamp: int | None
    max_clock_skew_seconds: int = 300


class ReplayRejected(ValueError):
    """Raised when replay checks fail closed."""


def require_replay_guard(
    *,
    transport_auth_mode: str,
    replay: ReplayCheck,
    shared_nonce_store_configured: bool,
) -> None:
    """Fail closed for transports that need replay protection.

    Trusted in-process or gateway-key wrappers can be exempt if they are
    protected out of band. External transports must provide nonce/timestamp and
    must be backed by a shared nonce store before they can be accepted.
    """

    if transport_auth_mode == "trusted-gateway-key":
        return
    if not replay.request_nonce or replay.request_timestamp is None:
        raise ReplayRejected("nonce and timestamp are required")
    if abs(int(time()) - int(replay.request_timestamp)) > replay.max_clock_skew_seconds:
        raise ReplayRejected("timestamp is outside the allowed clock skew")
    if not shared_nonce_store_configured:
        raise ReplayRejected("shared replay nonce store is not configured")

