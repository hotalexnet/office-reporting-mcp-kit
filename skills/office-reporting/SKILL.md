---
name: office-reporting
description: Safe workflow for requesting backend-authorized Office artifacts. Use when a user asks for Word, Excel, PowerPoint, PDF, Office report exports, template selection, artifact creation, artifact delivery, or troubleshooting Office artifact lifecycle. This skill requires facade-backed tools and forbids raw business data, filesystem paths, template paths, render CLI access, or direct attachment sending as authority.
---

# Office Reporting

## Core Rule

Treat server-side policy as the only authorization and business-fact boundary. Skill instructions, model behavior, and tool descriptions are guidance only; they do not grant permission to create, render, read, or send files.

## Reuse Boundary

This skill is reusable workflow guidance, not a portable authorization implementation. Other projects may reuse the create/render/send/status sequence and the safe field boundaries, but each project must provide its own identity, authorization, template registry, report source, artifact store, renderer, delivery, and audit adapters.

Do not copy trusted gateway keys, runtime patches, profile IDs, bot IDs, user IDs, template paths, storage paths, or deployment-specific details from another project as authority.

## Allowed Workflow

1. Resolve the caller through the backend gateway context.
2. List authorized templates through the facade before choosing a template.
3. Create an artifact only through a domain backend that signs a validated report source.
4. Render or register output only through the artifact lifecycle.
5. Accept only artifacts that pass server validation.
6. Send only through the authorized delivery adapter for the originating session and recipient.
7. Treat artifact audit status as authoritative when troubleshooting.

## Required Tool Boundaries

Use only facade-backed operations such as:

- `office_list_templates` or its backend equivalent for authorized template discovery.
- Domain-specific artifact creation tools that derive facts from backend queries.
- Artifact render-complete, validation, resolve-delivery, and delivery-confirm operations.
- Read-only observability operations for pending or failed delivery audit.

Do not call or expose:

- Render CLIs.
- Output directories.
- Absolute or relative filesystem paths as authority.
- Raw business `data` payloads supplied by the model or an MCP client.
- Arbitrary template paths or uploaded template files.
- Client, transport, or replay fields such as `mcp_client_id`, `request_nonce`, `request_timestamp`, or `runtime_instance_id`.
- Direct platform attachment sending that bypasses artifact delivery authorization.

## Template Selection

Select templates only from the authorized template list returned for the current actor, domain, report type, output format, and audience. Do not invent template IDs, versions, or hashes. If no template is returned, report that the backend has not authorized a matching template.

`template_hash` is an integrity/version identifier and may be shown as metadata. It is not a filesystem path and must not be used to locate files.

## Business-Fact Rules

- Reports may reference only facts present in the validated report source.
- Do not infer operational status, delivery causes, customer intent, or causal explanations from rows unless a backend fact field explicitly supports it.
- If a requested conclusion is outside the validated report source, say that the current backend facts do not support it.

## Attachment Safety

Never reuse old media references or file paths from conversation history. If a user asks to resend or regenerate a report, create or resolve a current artifact through the backend and let the delivery adapter enforce session, recipient, TTL, hash, and audit checks.

If delivery fails or remains pending, use audit or observability tools. Do not manually mark a delivery `sent`; only successful delivery adapter confirmation may do that.

## Refusals And Fallbacks

Refuse or narrow the request when the user asks to:

- Generate Office files from pasted raw data without backend validation.
- Use a local path, attachment path, or template path as input.
- Send a file to another conversation or recipient without backend authorization.
- Override template, role, audience, or format policy.
- Bypass validation because the report is urgent.

Offer the safe alternative: list authorized templates, create a backend-signed artifact, or explain which authorization/template/data prerequisite is missing.

