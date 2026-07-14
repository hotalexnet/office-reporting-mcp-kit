"""Model-facing contract boundary helpers."""

from __future__ import annotations

from collections.abc import Iterable, Mapping


FORBIDDEN_MODEL_ARGS = frozenset(
    {
        "context",
        "profile_id",
        "bot_id",
        "wecom_user_id",
        "conversation_id",
        "session_id",
        "chat_type",
        "source_message_id",
        "request_nonce",
        "request_timestamp",
        "runtime_instance_id",
        "domain",
        "role_name",
        "actor_user_id",
        "mcp_client_id",
        "allowed_profiles",
        "department",
        "authorized",
        "data",
        "raw_data",
        "template_path",
        "output_path",
        "media_tag",
        "storage_key",
        "source_hash",
        "snapshot_id",
        "render_key",
        "renderer_version",
        "render_cli",
        "recipient",
        "delivery_request_id",
        "mark_sent",
    }
)


class ModelControlledFieldError(ValueError):
    """Raised when a model-visible request includes server-controlled fields."""


def reject_model_controlled_fields(
    args: Mapping[str, object],
    *,
    allowed_args: Iterable[str],
    forbidden_args: frozenset[str] = FORBIDDEN_MODEL_ARGS,
) -> None:
    """Reject forbidden or undeclared model-visible arguments.

    Use this in addition to JSON Schema ``additionalProperties: false``. Schema
    enforcement catches normal client misuse; this function is the runtime
    fail-closed guard for wrappers and adapters.
    """

    allowed = set(allowed_args)
    provided = set(args)
    forbidden = sorted(provided & forbidden_args)
    unknown = sorted(provided - allowed)
    if forbidden:
        raise ModelControlledFieldError(
            "Model request included server-controlled fields: "
            + ", ".join(forbidden)
        )
    if unknown:
        raise ModelControlledFieldError(
            "Model request included unsupported fields: " + ", ".join(unknown)
        )

