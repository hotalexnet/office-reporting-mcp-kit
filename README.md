# Office Reporting MCP Kit

Reusable Office artifact workflow and MCP contract for backend-authorized
Word, Excel, PowerPoint, and PDF reporting.

This repository contains the portable parts of an Office reporting module:

- Skill workflow guidance for LLM/agent use.
- A machine-readable MCP tool contract manifest.
- Adapter contracts for identity, authorization, template registry, report
  source, artifact store, renderer, delivery, and audit.
- Minimal Python helpers for lifecycle data structures and boundary checks.

It deliberately does not include any project-specific credentials, user IDs,
runtime patches, database rows, storage paths, or business report
implementations.

## Core Workflow

```text
office_list_templates
office_create_report
office_render_report
office_send_report
delivery adapter confirms sent only after platform success
```

The model never supplies identity, authorization conclusions, raw business
data, template paths, output paths, renderer commands, recipients, media tags,
or delivery confirmation fields.

## How To Reuse In Another Project

1. Copy or install `skills/office-reporting/SKILL.md` into your agent skill
   system.
2. Start from `contracts/office-reporting-mcp.manifest.json` and replace the
   example enum values with your project's server-defined values.
3. Implement the adapter protocols in `python/office_reporting/adapters.py`.
4. Keep all identity and authorization fields server-side.
5. Query business facts from your backend and sign or hash the validated
   source before rendering.
6. Render only through your artifact lifecycle service.
7. Confirm delivery only after the target platform reports successful send.
8. Add tests that bind your tool schemas to the manifest and forbidden fields.

See `docs/integration-guide-cn.md` for the detailed checklist.

## Repository Layout

```text
skills/office-reporting/SKILL.md
contracts/office-reporting-mcp.manifest.json
contracts/examples/finance-office-reporting.manifest.json
docs/
python/office_reporting/
tests/
```

## Install For Local Development

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests
```

## Security Boundary

The reusable contract is not an authorization implementation. Each project
must provide its own trusted gateway, actor resolver, client registry,
transport authentication, replay protection, template policy, source signing,
artifact store, renderer validation, delivery confirmation, and audit store.

