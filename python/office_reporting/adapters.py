"""Project adapter protocols for reusable Office Reporting workflows."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any, Protocol

from .lifecycle import (
    ActorContext,
    ArtifactIntent,
    ArtifactMetadata,
    DeliveryReservation,
    RecipientContext,
    ValidatedReportSource,
)


class IdentityAdapter(Protocol):
    def actor_context_from_runtime(self, invocation: Mapping[str, Any]) -> ActorContext:
        """Resolve caller identity from trusted runtime context, not model args."""


class AuthorizationAdapter(Protocol):
    def assert_can_create(
        self,
        actor: ActorContext,
        *,
        domain: str,
        report_type: str,
        output_format: str,
        audience: str,
        data_scope: Mapping[str, Any],
    ) -> None:
        """Raise if the actor is not authorized for this report intent."""


class TemplateRegistryAdapter(Protocol):
    def list_authorized_templates(
        self,
        actor: ActorContext,
        *,
        domain: str,
        report_type: str | None = None,
        output_format: str | None = None,
        audience: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return template metadata only; never return template paths."""


class ReportSourceAdapter(Protocol):
    def validated_source(
        self,
        actor: ActorContext,
        *,
        domain: str,
        report_type: str,
        data_scope: Mapping[str, Any],
    ) -> ValidatedReportSource:
        """Query backend facts and return a signed or hashed source reference."""


class ArtifactStoreAdapter(Protocol):
    def create_intent(
        self,
        actor: ActorContext,
        *,
        source: ValidatedReportSource,
        output_format: str,
        audience: str,
    ) -> ArtifactMetadata:
        """Create a backend-authorized artifact intent."""

    def render_intent(self, actor: ActorContext, *, artifact_id: str) -> ArtifactIntent:
        """Return render intent only if current actor/session is authorized."""

    def status(self, actor: ActorContext, *, artifact_id: str) -> ArtifactMetadata:
        """Return model-safe artifact metadata."""


class RendererAdapter(Protocol):
    def render(self, intent: ArtifactIntent, source: ValidatedReportSource) -> Path:
        """Render an artifact to a server-controlled path."""

    def validate(self, path: Path, *, output_format: str) -> None:
        """Raise if rendered output is invalid."""


class DeliveryAdapter(Protocol):
    def recipient_context_from_runtime(
        self, actor: ActorContext, invocation: Mapping[str, Any]
    ) -> RecipientContext:
        """Resolve recipient from trusted session context, not model args."""

    def reserve(
        self,
        actor: ActorContext,
        recipient: RecipientContext,
        *,
        artifact_id: str,
    ) -> DeliveryReservation:
        """Reserve delivery for the current actor/session/recipient."""

    def send_reserved(self, reservation: DeliveryReservation) -> None:
        """Send through the platform adapter; raise on failure."""

    def confirm_sent(self, reservation: DeliveryReservation) -> None:
        """Mark sent only after platform delivery succeeds."""


class AuditAdapter(Protocol):
    def record(self, event_type: str, fields: Mapping[str, Any]) -> None:
        """Record audit events without exposing audit context to the model."""

