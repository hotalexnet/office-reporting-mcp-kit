"""Reusable Office Reporting MCP contract helpers."""

from .adapters import (
    ArtifactStoreAdapter,
    AuditAdapter,
    AuthorizationAdapter,
    DeliveryAdapter,
    IdentityAdapter,
    RendererAdapter,
    ReportSourceAdapter,
    TemplateRegistryAdapter,
)
from .contracts import FORBIDDEN_MODEL_ARGS, reject_model_controlled_fields
from .lifecycle import (
    ActorContext,
    ArtifactIntent,
    ArtifactMetadata,
    DeliveryReservation,
    RecipientContext,
    ValidatedReportSource,
)
from .replay import ReplayCheck, ReplayRejected, require_replay_guard

__all__ = [
    "ActorContext",
    "ArtifactIntent",
    "ArtifactMetadata",
    "ArtifactStoreAdapter",
    "AuditAdapter",
    "AuthorizationAdapter",
    "DeliveryAdapter",
    "DeliveryReservation",
    "FORBIDDEN_MODEL_ARGS",
    "IdentityAdapter",
    "RecipientContext",
    "RendererAdapter",
    "ReplayCheck",
    "ReplayRejected",
    "ReportSourceAdapter",
    "TemplateRegistryAdapter",
    "ValidatedReportSource",
    "reject_model_controlled_fields",
    "require_replay_guard",
]

