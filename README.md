# Office Reporting MCP Kit

[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-yellow.svg)](https://www.apache.org/licenses/LICENSE-2.0)
[![Runtime: Python 3](https://img.shields.io/badge/runtime-python3-blue.svg)](https://www.python.org/)
[![Protocol: MCP](https://img.shields.io/badge/protocol-MCP-2ea44f.svg)](#standard-tool-workflow)
**English** | [**中文**](./README.zh-CN.md)

Reusable MCP contracts, Agent Skill guidance, and Python adapter protocols for Office report generation workflows.

This project is not an out-of-the-box reporting system, and it is not a renderer that directly writes data into Word, Excel, PowerPoint, or PDF files. It provides a safe, portable, and testable integration skeleton for Office Reporting MCP workflows. The goal is to help business systems expose report creation, rendering, and delivery to LLMs/Agents while keeping identity, authorization, business data, template paths, filesystem paths, and delivery confirmation under backend control.

## What This Project Is For

When an Agent can help users "generate a daily report", "export an Excel file", "create a PowerPoint deck", or "send a PDF", the main risk is usually not the file format itself. The main risk is the authorization boundary:

- The model must not decide who the user is.
- The model must not decide whether the user is allowed to export a report.
- Report data must come from trusted backend queries, not from model-generated facts or arbitrary raw data pasted by a user.
- Templates, output paths, renderer commands, and storage keys must not be exposed to the model.
- Attachment recipients must come from the current session or platform context, not from model-controlled arguments.
- The backend may mark delivery as `sent` only after the target platform confirms successful delivery.

This project addresses those boundaries by splitting Office report workflows into standard MCP tools and providing a manifest, Skill instructions, adapter protocols, runtime boundary checks, and tests that can be reused in other business systems.

## What It Does

This repository provides these reusable pieces:

- `skills/office-reporting/SKILL.md`: safe Office reporting workflow guidance for LLMs/Agents.
- `contracts/office-reporting-mcp.manifest.json`: machine-readable MCP tool contract manifest.
- `contracts/examples/finance-office-reporting.manifest.json`: example manifest for finance reporting.
- `python/office_reporting/adapters.py`: Adapter Protocols that a project must implement.
- `python/office_reporting/contracts.py`: forbidden model field checks for model-visible arguments.
- `python/office_reporting/lifecycle.py`: artifact lifecycle data structures.
- `python/office_reporting/replay.py`: transport replay guard skeleton.
- `tests/test_contracts.py`: sample tests for manifest binding, forbidden fields, and replay guard behavior.
- `docs/`: Chinese integration guide, contract notes, and security hardening checklist.

Using these pieces, a project can implement:

- Listing Office templates authorized for the current user.
- Creating backend-authorized report artifact intents.
- Rendering Word, Excel, PowerPoint, or PDF artifacts from backend-signed data snapshots.
- Querying artifact lifecycle status.
- Sending artifacts through a controlled delivery adapter to WeCom, chat sessions, email, or other platforms.
- Testing MCP schemas, manifests, and forbidden fields so future changes do not expose sensitive controls to the model.

## What It Does Not Do

This project intentionally does not provide:

- Project-specific users, profiles, bots, roles, departments, or authorization policies.
- Database queries, business report SQL, or business data implementations.
- Real template files, template paths, output paths, or storage paths.
- Renderer CLI wrappers, LibreOffice/Office conversion commands, or document conversion services.
- Real WeCom, email, or platform delivery implementations.
- A ready-to-deploy MCP Server.
- Credentials, gateway keys, tokens, accounts, or runtime patches.

In short, this project provides the safe contract and integration skeleton. The real identity, authorization, source query, renderer, artifact store, delivery, and audit implementations must come from your business project.

## Standard Tool Workflow

The recommended MCP tool workflow is:

```text
office_list_templates
office_create_report
office_render_report
office_get_artifact_status
office_send_report
platform delivery confirm
```

Typical flow:

1. The Agent calls `office_list_templates` and sees only template metadata authorized for the current actor.
2. The Agent selects a report type, format, audience, and controlled scope based on the user request.
3. The Agent calls `office_create_report` to create an artifact intent.
4. The backend resolves the actor again, authorizes the request, queries business facts, and issues a source hash/snapshot.
5. The Agent calls `office_render_report`.
6. The backend renders through a controlled renderer into a server-owned path and validates the output file.
7. The Agent calls `office_get_artifact_status` to check lifecycle status.
8. The Agent calls `office_send_report` to request delivery.
9. The delivery adapter sends through the current runtime/session/recipient context.
10. The backend marks delivery `sent` only after the platform confirms successful delivery.

## MCP Tool Reference

### `office_list_templates`

Lists Office templates authorized by the server for the current actor.

Model-visible fields are defined by the project manifest. Typical fields are:

```text
report_type
output_format
audience
```

Responses should contain only model-safe template metadata, such as template id, version, display name, supported format, audience, and hash.

Never return:

```text
template_path
storage_key
renderer command
filesystem path
raw business data
```

### `office_create_report`

Creates a backend-authorized artifact intent.

Model-visible parameters must be project-defined closed enums or controlled filters, such as:

```text
report_type
output_format
audience
scope
entity_code
start_date
end_date
currency
```

The backend must:

- Resolve actor identity from runtime context.
- Re-run authorization.
- Query business facts from the backend.
- Generate `snapshot_id` and `source_hash`.
- Select an authorized template version.
- Create the artifact intent.

The model must not provide:

```text
data
raw_data
template_path
output_path
source_hash
snapshot_id
recipient
mark_sent
```

### `office_render_report`

Renders and validates an authorized artifact.

The model should provide only:

```text
artifact_id
```

The backend must re-check whether the current actor/session can render the artifact and then generate the file through the renderer adapter. Render output paths, renderer CLI, and storage keys must remain hidden from the model.

### `office_get_artifact_status`

Queries lifecycle status for an artifact readable by the current actor/session.

The model should provide only:

```text
artifact_id
```

Responses should use an allow-list and include only model-safe fields, such as:

```text
artifact_id
validation_status
lifecycle_status
report_type
output_format
audience
template_id
template_version
created_at
expires_at
```

Do not return storage keys, filesystem paths, media references, source hashes, actor context, or recipient context.

### `office_send_report`

Requests delivery of a rendered artifact to the currently authorized recipient.

The model should provide only:

```text
artifact_id
```

The recipient must be resolved by the delivery adapter from trusted runtime/session/platform context. The model must not provide the recipient. Delivery may be confirmed as sent only after the target platform reports success.

## Fields The Model Must Not Control

`contracts/office-reporting-mcp.manifest.json` and `python/office_reporting/contracts.py` jointly maintain the forbidden fields list.

The model or MCP client must not provide these fields:

```text
context
profile_id
bot_id
wecom_user_id
conversation_id
session_id
chat_type
source_message_id
request_nonce
request_timestamp
runtime_instance_id
domain
role_name
actor_user_id
mcp_client_id
allowed_profiles
department
authorized
data
raw_data
template_path
output_path
media_tag
storage_key
source_hash
snapshot_id
render_key
renderer_version
render_cli
recipient
delivery_request_id
mark_sent
```

Project implementations must use two layers of protection:

1. Set `additionalProperties: false` in MCP tool schemas.
2. Call `reject_model_controlled_fields()` in wrappers/runtime code, or implement an equivalent fail-closed check.

## Adapter Architecture

A project must implement the protocols in `python/office_reporting/adapters.py`.

| Adapter | Responsibility | Boundary |
|---|---|---|
| `IdentityAdapter` | Resolve the current actor from trusted runtime context | Must not read identity from model arguments |
| `AuthorizationAdapter` | Decide whether the actor may create a report | Must not trust model-provided role/authorized fields |
| `TemplateRegistryAdapter` | Return template metadata authorized for the current actor | Must not return template paths |
| `ReportSourceAdapter` | Query backend business facts and issue a validated source | Must not use model-provided raw data |
| `ArtifactStoreAdapter` | Manage intent, status, render authorization, and lifecycle | Must not allow cross-user access by artifact id alone |
| `RendererAdapter` | Render and validate output files | Must not expose renderer CLI or output paths |
| `DeliveryAdapter` | Resolve recipient, reserve delivery, send, and confirm | Must not accept model-provided recipient/mark_sent |
| `AuditAdapter` | Record client/runtime/session/tool/artifact/delivery audit events | Must not pass internal audit context through to the model |

## Repository Layout

```text
.
├── README.md
├── README.zh-CN.md
├── pyproject.toml
├── contracts/
│   ├── office-reporting-mcp.manifest.json
│   └── examples/
│       └── finance-office-reporting.manifest.json
├── docs/
│   ├── contract-and-adapter-cn.md
│   ├── integration-guide-cn.md
│   └── security-hardening-cn.md
├── python/
│   └── office_reporting/
│       ├── __init__.py
│       ├── adapters.py
│       ├── contracts.py
│       ├── lifecycle.py
│       └── replay.py
├── skills/
│   └── office-reporting/
│       └── SKILL.md
└── tests/
    └── test_contracts.py
```

## Installation And Local Development

Requirements:

- Python 3.11+
- pip

Install as an editable package:

```bash
python3 -m pip install -e .
```

Run tests:

```bash
python3 -m unittest discover -s tests
```

Current tests cover:

- `forbidden_model_args` in the manifest matches the Python constant.
- Forbidden fields are rejected by runtime checks.
- Undeclared fields are rejected by runtime checks.
- Trusted gateway transport can skip the replay guard.
- External transport fails closed when the shared nonce store is missing.

## How To Use In A Project

### 1. Copy The Skill

Copy or install:

```text
skills/office-reporting/SKILL.md
```

into your Agent/LLM skill system.

The Skill tells the model:

- Use only backend-authorized Office artifact tools.
- Do not pass raw business data.
- Do not use paths, template paths, or renderer CLI.
- Do not decide whether delivery succeeded.
- Narrow the request or explain missing prerequisites when authorization or templates are unavailable.

### 2. Define A Project Manifest

Start from the generic manifest:

```text
contracts/office-reporting-mcp.manifest.json
```

Replace example enums with your business-owned closed sets.

For a finance example, see:

```text
contracts/examples/finance-office-reporting.manifest.json
```

Example report types:

```text
balances
transactions
income_expense_summary
entity_comparison
```

Example output formats:

```text
docx
xlsx
pptx
pdf
```

Example audience values:

```text
internal
external
archive
```

Note: `domain` is not recommended as a model-visible argument. It should be fixed by the project adapter, server-side route, or MCP server configuration.

### 3. Bind MCP Tool Schemas

Each MCP tool JSON Schema should match the manifest and at least include:

```json
{
  "additionalProperties": false
}
```

Add tests to ensure the actual tool schema, manifest, and forbidden fields do not drift apart.

### 4. Implement Adapters

Implement these protocols in your project:

```python
from office_reporting.adapters import (
    IdentityAdapter,
    AuthorizationAdapter,
    TemplateRegistryAdapter,
    ReportSourceAdapter,
    ArtifactStoreAdapter,
    RendererAdapter,
    DeliveryAdapter,
    AuditAdapter,
)
```

These protocols define boundaries and responsibilities only. They do not bind you to a specific database, messaging platform, object store, template engine, or renderer.

### 5. Reject Model-Controlled Fields In Wrappers

Example:

```python
from office_reporting.contracts import reject_model_controlled_fields

def office_create_report(args, runtime):
    reject_model_controlled_fields(
        args,
        allowed_args={
            "report_type",
            "output_format",
            "audience",
            "scope",
        },
    )
    # Resolve actor from runtime, authorize, query source, create artifact...
```

### 6. Add Replay Guard

If the MCP transport is not a trusted in-process/gateway-key mode, it needs nonce, timestamp, and a shared nonce store.

Example:

```python
from office_reporting.replay import ReplayCheck, require_replay_guard

require_replay_guard(
    transport_auth_mode=runtime.transport_auth_mode,
    replay=ReplayCheck(
        request_nonce=runtime.request_nonce,
        request_timestamp=runtime.request_timestamp,
    ),
    shared_nonce_store_configured=True,
)
```

### 7. Run A Real Smoke Test

Before enabling the flow in production, verify at least:

```text
list templates
create artifact intent
render artifact
validate artifact
send artifact
platform confirms sent
status/audit can explain result
```

If any step does not have a real backend implementation, enable only read-only capabilities such as list/status. Do not enable create/render/send.

## Minimal Pseudocode Example

This simplified wrapper shows the boundary. It is not a full implementation:

```python
def office_create_report(args, runtime, adapters):
    reject_model_controlled_fields(
        args,
        allowed_args={"report_type", "output_format", "audience", "scope"},
    )

    actor = adapters.identity.actor_context_from_runtime(runtime)
    adapters.authorization.assert_can_create(
        actor,
        domain="finance",
        report_type=args["report_type"],
        output_format=args["output_format"],
        audience=args["audience"],
        data_scope=args.get("scope", {}),
    )
    source = adapters.report_source.validated_source(
        actor,
        domain="finance",
        report_type=args["report_type"],
        data_scope=args.get("scope", {}),
    )
    artifact = adapters.artifact_store.create_intent(
        actor,
        source=source,
        output_format=args["output_format"],
        audience=args["audience"],
    )
    adapters.audit.record("office_report_created", {"artifact_id": artifact.artifact_id})
    return {
        "artifact_id": artifact.artifact_id,
        "validation_status": artifact.validation_status,
        "lifecycle_status": artifact.lifecycle_status,
        "report_type": artifact.report_type,
        "output_format": artifact.output_format,
        "audience": artifact.audience,
    }
```

## Security Principles

Integrating projects must preserve these invariants:

1. Server-side policy is the only authorization boundary.
2. Identity/context fields must not enter model-fillable schemas.
3. `domain` is fixed by the project adapter or server-side route, not by the model.
4. Business facts are queried and signed by the backend, not supplied as model raw data.
5. Templates come only from the authorized template registry, not model-provided paths.
6. Responses use allow-lists and must not pass through internal service views.
7. Delivery is confirmed as `sent` only by the adapter after platform success.
8. Media references are not permission tokens and must not be reused from conversation history.

More details:

- `docs/integration-guide-cn.md`
- `docs/contract-and-adapter-cn.md`
- `docs/security-hardening-cn.md`

## FAQ

### Can this project directly generate Word/Excel/PowerPoint/PDF files?

No. It does not include a real renderer or template files. You need to implement `RendererAdapter` in your project and connect it to your Office rendering service, LibreOffice, template engine, or document generation pipeline.

### Why can't the model provide `template_path` or `output_path`?

Paths are part of the server-side permission boundary. If the model controls paths, it may read or overwrite unauthorized files. Template selection must come from a backend-authorized template registry, and output paths must be controlled by the artifact store/renderer.

### Why can't the model provide `raw_data`?

Business facts in reports must come from trusted backend queries and signed sources. Model-provided raw data bypasses business authorization, data audit, source hash, and drift checks.

### Why can't `office_send_report` accept recipient?

Recipient must be resolved from the current platform session or backend authorization context. A model-provided recipient can bypass session and platform authorization and may cause cross-session or cross-user delivery.

### Can I use only part of this kit?

Yes. The safest incremental path is to start with read-only tools:

```text
office_list_templates
office_get_artifact_status
```

After identity, authorization, audit, and schema binding tests are complete, enable create/render/send.

### How do I add a new report type?

For every new `report_type`, add at least:

- manifest enum
- MCP tool schema enum
- template/policy provisioning
- backend source query
- source hash or snapshot signing
- renderer support
- response allow-list test
- forbidden fields test
- real platform send smoke test

## License

This project is licensed under the Apache License, Version 2.0. See `LICENSE` for details.
