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

---

# Office Reporting MCP Kit 中文说明

这是一个可复用的 Office artifact 工作流和 MCP 契约，用于由后端授权的
Word、Excel、PowerPoint、PDF 报告生成与发送。

本仓库只包含 Office Reporting 模块中可跨项目复用的部分：

- 给 LLM/agent 使用的 Skill 工作流说明。
- 机器可读的 MCP tool contract manifest。
- identity、authorization、template registry、report source、artifact store、
  renderer、delivery、audit 等 adapter 契约。
- 最小 Python 辅助代码：生命周期数据结构、forbidden fields 检查、replay guard 骨架。

本仓库刻意不包含任何项目私有凭证、用户 ID、runtime patch、数据库策略行、
存储路径或业务报表实现。

## 核心链路

```text
office_list_templates
office_create_report
office_render_report
office_send_report
delivery adapter 仅在平台真实发送成功后确认 sent
```

模型永远不能提供 identity、授权结论、原始业务数据、模板路径、输出路径、
renderer 命令、收件人、media tag 或 delivery 确认字段。

## 如何在其他项目复用

1. 把 `skills/office-reporting/SKILL.md` 复制或安装到目标 agent skill 系统。
2. 从 `contracts/office-reporting-mcp.manifest.json` 开始，把示例 enum 替换成项目服务端定义的闭集。
3. 实现 `python/office_reporting/adapters.py` 中的 adapter protocol。
4. 所有 identity 和 authorization 字段都必须由服务端注入或解析。
5. 业务事实必须由后端查询，并在渲染前签发或计算 source hash。
6. 只能通过 artifact lifecycle service 渲染。
7. 只有目标平台报告发送成功后，才能确认 delivery sent。
8. 添加测试，把项目 tool schema、manifest 和 forbidden fields 绑定起来，防止漂移。

详细接入清单见 `docs/integration-guide-cn.md`。

## 仓库结构

```text
skills/office-reporting/SKILL.md
contracts/office-reporting-mcp.manifest.json
contracts/examples/finance-office-reporting.manifest.json
docs/
python/office_reporting/
tests/
```

## 本地开发安装

```bash
python3 -m pip install -e .
python3 -m unittest discover -s tests
```

## 安全边界

这个可复用契约不是授权实现。每个项目都必须提供自己的 trusted gateway、
actor resolver、client registry、transport authentication、replay protection、
template policy、source signing、artifact store、renderer validation、
delivery confirmation 和 audit store。
