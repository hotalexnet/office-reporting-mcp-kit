"""Portable lifecycle data structures for Office artifacts."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ActorContext:
    actor_user_id: str
    role_name: str
    profile_id: str
    session_id: str
    conversation_id: str
    client_id: str
    transport_auth_mode: str
    runtime_instance_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RecipientContext:
    recipient_id: str
    session_id: str
    conversation_id: str
    chat_type: str
    client_id: str
    transport_auth_mode: str
    runtime_instance_id: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ValidatedReportSource:
    domain: str
    report_type: str
    snapshot_id: str
    source_hash: str
    data_scope: dict[str, Any]


@dataclass(frozen=True)
class ArtifactIntent:
    artifact_id: str
    domain: str
    report_type: str
    output_format: str
    audience: str
    source_hash: str
    data_scope: dict[str, Any]
    template_id: str
    template_version: str


@dataclass(frozen=True)
class ArtifactMetadata:
    artifact_id: str
    validation_status: str
    lifecycle_status: str
    domain: str
    report_type: str
    output_format: str
    audience: str
    template_id: str
    template_version: str
    created_at: datetime | None = None
    expires_at: datetime | None = None


@dataclass(frozen=True)
class DeliveryReservation:
    delivery_id: str
    delivery_status: str
    media_ref: str | None = None

