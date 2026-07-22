# Office Reporting MCP Kit

[English README](README.md)

面向 Office 报告生成场景的可复用 MCP 契约、Agent Skill 和 Python Adapter 协议。

这个项目不是一个开箱即用的报表系统，也不是一个直接把数据写进 Word/Excel/PPT/PDF 的渲染器。它提供的是一套安全、可迁移、可测试的“Office 报告 MCP 接入骨架”，用于帮助其他业务系统把报告生成、渲染、发送流程接入到 LLM/Agent，同时把身份、授权、业务数据、模板路径、文件路径和发送确认牢牢留在后端控制边界内。

## 项目有什么用

当一个 Agent 可以帮用户“生成日报、导出 Excel、制作 PPT、发送 PDF”时，最危险的地方通常不是文件格式本身，而是权限边界：

- 用户是谁，模型不能自己说了算。
- 用户有没有权限导出某类报表，模型不能自己判断。
- 报表数据必须来自后端可信查询，不能来自模型编造或用户粘贴的任意 raw data。
- 模板、输出路径、渲染命令、存储 key 不能暴露给模型。
- 附件发送对象必须来自当前会话或平台上下文，不能让模型任意指定 recipient。
- 只有平台真实发送成功后，后端才能确认 delivery sent。

本项目解决的是这些边界问题：它把 Office 报告流程拆成标准 MCP 工具链路，并给出 manifest、Skill 指南、Adapter 协议、运行时边界检查和测试样例，方便你在自己的业务系统里复用。

## 能做什么

本项目提供以下可复用内容：

- `skills/office-reporting/SKILL.md`：给 LLM/Agent 使用的 Office 报告安全工作流说明。
- `contracts/office-reporting-mcp.manifest.json`：机器可读的 MCP tool contract manifest。
- `contracts/examples/finance-office-reporting.manifest.json`：财务报表场景示例 manifest。
- `python/office_reporting/adapters.py`：项目侧需要实现的 Adapter Protocol。
- `python/office_reporting/contracts.py`：模型可见参数的 forbidden fields 检查。
- `python/office_reporting/lifecycle.py`：artifact 生命周期相关数据结构。
- `python/office_reporting/replay.py`：传输 replay guard 骨架。
- `tests/test_contracts.py`：manifest 与 Python 常量绑定、forbidden fields、replay guard 的测试样例。
- `docs/`：中文接入指南、契约说明和安全加固清单。

基于这些内容，你可以在自己的系统中实现：

- 列出当前用户被授权使用的 Office 模板。
- 创建后端授权的报表 artifact intent。
- 基于后端签发的数据快照渲染 Word、Excel、PowerPoint 或 PDF。
- 查询 artifact 生命周期状态。
- 通过受控 delivery adapter 把 artifact 发送到企业微信、聊天会话、邮件或其他平台。
- 用测试锁住 MCP schema、manifest 和 forbidden fields，防止后续开发把敏感字段暴露给模型。

## 不能做什么

本项目刻意不提供以下内容：

- 不提供项目私有用户、profile、bot、角色、部门或权限策略。
- 不提供数据库查询、业务报表 SQL 或业务数据实现。
- 不提供真实模板文件、模板路径、输出路径或存储路径。
- 不提供 renderer CLI、LibreOffice/Office 转换命令封装。
- 不提供企业微信、邮件或其他平台的真实发送实现。
- 不提供可直接部署的 MCP Server。
- 不提供任何 credentials、gateway key、token、账号或 runtime patch。

也就是说，本项目提供的是“安全契约和接入骨架”，真正的 identity、authorization、source query、renderer、artifact store、delivery、audit 都必须由你的业务项目自己实现。

## 标准工具链路

推荐的 MCP 工具链路是：

```text
office_list_templates
office_create_report
office_render_report
office_get_artifact_status
office_send_report
platform delivery confirm
```

典型流程：

1. Agent 调用 `office_list_templates`，只看到当前 actor 被授权的模板 metadata。
2. Agent 根据用户需求选择 report type、format、audience 和受控 scope。
3. Agent 调用 `office_create_report` 创建 artifact intent。
4. 后端重新解析 actor，执行授权，查询业务事实，签发 source hash/snapshot。
5. Agent 调用 `office_render_report`。
6. 后端通过受控 renderer 渲染到服务端路径，并校验输出文件。
7. Agent 调用 `office_get_artifact_status` 查询状态。
8. Agent 调用 `office_send_report` 请求发送。
9. delivery adapter 根据当前 runtime/session/recipient 做发送。
10. 只有平台确认发送成功后，后端才能标记 `sent`。

## MCP 工具说明

### `office_list_templates`

列出当前 actor 被服务端授权的 Office 模板。

模型可传的字段由项目 manifest 决定，通常是：

```text
report_type
output_format
audience
```

返回值应该只包含模型安全的模板 metadata，例如 template id、version、display name、支持的 format、audience、hash 等。

禁止返回：

```text
template_path
storage_key
renderer command
filesystem path
raw business data
```

### `office_create_report`

创建后端授权的 artifact intent。

模型可见参数只能是项目定义的闭集或受控 filter，例如：

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

后端必须完成：

- 从 runtime 解析 actor。
- 重新执行 authorization。
- 从后端查询业务事实。
- 生成 `snapshot_id` 和 `source_hash`。
- 选择授权模板版本。
- 创建 artifact intent。

模型不能传：

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

渲染并校验已授权 artifact。

模型只应传：

```text
artifact_id
```

后端必须重新确认当前 actor/session 是否可以渲染该 artifact，并通过 renderer adapter 生成文件。渲染输出路径、renderer CLI、storage key 仍然不能暴露给模型。

### `office_get_artifact_status`

查询当前 actor/session 可读 artifact 的生命周期状态。

模型只应传：

```text
artifact_id
```

返回值应该使用 allow-list，只返回模型安全字段，例如：

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

不能返回 storage key、文件路径、media reference、source hash、actor context 或 recipient context。

### `office_send_report`

请求把已渲染 artifact 发送到当前授权 recipient。

模型只应传：

```text
artifact_id
```

recipient 必须由 delivery adapter 从可信 runtime/session/platform context 中解析，不能由模型提供。delivery 只能在真实平台发送成功后确认 sent。

## 模型禁止控制的字段

`contracts/office-reporting-mcp.manifest.json` 和 `python/office_reporting/contracts.py` 共同维护 forbidden fields。

模型或 MCP client 不应该传递这些字段：

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

项目实现必须双层防护：

1. MCP tool schema 设置 `additionalProperties: false`。
2. wrapper/runtime 调用 `reject_model_controlled_fields()` 或实现等价的 fail-closed 检查。

## Adapter 架构

项目接入时需要实现 `python/office_reporting/adapters.py` 中的协议。

| Adapter | 职责 | 关键边界 |
|---|---|---|
| `IdentityAdapter` | 从可信 runtime context 解析当前 actor | 不能从模型参数读取身份 |
| `AuthorizationAdapter` | 判断 actor 是否可创建某类报告 | 不能信任模型传入 role/authorized |
| `TemplateRegistryAdapter` | 返回当前 actor 被授权模板 metadata | 不能返回模板路径 |
| `ReportSourceAdapter` | 查询后端业务事实并签发 source | 不能使用模型 raw data |
| `ArtifactStoreAdapter` | 管理 intent、status、render 授权和生命周期 | 不能仅凭 artifact id 跨用户读取 |
| `RendererAdapter` | 渲染并校验输出文件 | 不能暴露 renderer CLI 或输出路径 |
| `DeliveryAdapter` | 解析 recipient、reserve、send、confirm | 不能接收模型 recipient/mark_sent |
| `AuditAdapter` | 记录 client/runtime/session/tool/artifact/delivery 审计 | 不能把审计上下文透传给模型 |

## 仓库结构

```text
.
├── README.md
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

## 安装与本地开发

要求：

- Python 3.11+
- pip

安装为可编辑包：

```bash
python3 -m pip install -e .
```

运行测试：

```bash
python3 -m unittest discover -s tests
```

当前测试覆盖：

- manifest 中的 `forbidden_model_args` 与 Python 常量一致。
- forbidden fields 会被运行时检查拒绝。
- 未声明字段会被运行时检查拒绝。
- trusted gateway transport 可以跳过 replay guard。
- 外部 transport 缺少共享 nonce store 时 fail closed。

## 如何在项目中使用

### 1. 复制 Skill

把：

```text
skills/office-reporting/SKILL.md
```

复制或安装到你的 Agent/LLM skill 系统中。

这个 Skill 告诉模型：

- 只能走后端授权的 Office artifact 工具。
- 不能传 raw business data。
- 不能使用路径、模板路径或 renderer CLI。
- 不能自己判断发送成功。
- 出现权限或模板缺失时应该收窄请求或说明缺失前置条件。

### 2. 定义项目 manifest

从通用模板开始：

```text
contracts/office-reporting-mcp.manifest.json
```

然后把示例 enum 替换成你的业务闭集。

例如财务场景可以参考：

```text
contracts/examples/finance-office-reporting.manifest.json
```

示例 report types：

```text
balances
transactions
income_expense_summary
entity_comparison
```

示例 output formats：

```text
docx
xlsx
pptx
pdf
```

示例 audience：

```text
internal
external
archive
```

注意：`domain` 不建议作为模型可见参数。它应该由项目 adapter、服务端路由或 MCP server 配置固定。

### 3. 绑定 MCP tool schema

每个 MCP tool 的 JSON Schema 应该和 manifest 保持一致，至少满足：

```json
{
  "additionalProperties": false
}
```

建议添加测试，确保实际 tool schema、manifest 和 forbidden fields 不会漂移。

### 4. 实现 Adapter

在你的项目中实现这些协议：

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

这些协议只定义边界和职责，不绑定具体数据库、消息平台、对象存储、模板引擎或 renderer。

### 5. 在 wrapper 中拒绝模型控制字段

示例：

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

### 6. 接入 replay guard

如果 MCP transport 不是可信的 in-process/gateway-key 模式，就需要 nonce、timestamp 和共享 nonce store。

示例：

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

### 7. 做真实 smoke test

上线前至少跑通：

```text
list templates
create artifact intent
render artifact
validate artifact
send artifact
platform confirms sent
status/audit can explain result
```

如果其中任一步没有真实后端实现，只能启用只读能力，例如 list/status，不能启用 create/render/send。

## 最小伪代码示例

下面是一个简化 wrapper 结构，仅用于说明边界，不是完整实现：

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

## 安全原则

接入项目必须遵守这些不变量：

1. 服务端 policy 是唯一授权边界。
2. identity/context 不进入模型可填写 schema。
3. `domain` 由项目 adapter 或服务端路由固定，不能让模型自由传。
4. 业务事实由后端查询和签发，不能使用模型 raw data。
5. 模板只能来自授权 template registry，不能使用模型传入路径。
6. response 必须使用 allow-list，不能透传内部 service view。
7. delivery 只能由 adapter 在平台发送成功后确认 `sent`。
8. media reference 不是权限凭证，不能从历史对话复用。

详细说明见：

- `docs/integration-guide-cn.md`
- `docs/contract-and-adapter-cn.md`
- `docs/security-hardening-cn.md`

## 常见问题

### 这个项目能直接生成 Word/Excel/PPT/PDF 吗？

不能。它不包含真实 renderer 或模板文件。你需要在项目中实现 `RendererAdapter`，并接入自己的 Office 渲染服务、LibreOffice、模板引擎或文档生成管线。

### 为什么不允许模型传 `template_path` 或 `output_path`？

因为路径是服务端权限边界的一部分。模型一旦能控制路径，就可能读取或覆盖非授权文件。模板选择必须来自后端授权的 template registry，输出路径必须由 artifact store/renderer 控制。

### 为什么不允许模型传 `raw_data`？

报告里的业务事实必须来自后端可信查询和签发。模型传入 raw data 会绕过业务权限、数据审计、source hash 和 drift check。

### 为什么 `office_send_report` 不允许传 recipient？

recipient 必须由当前平台会话或后端授权上下文解析。模型指定 recipient 会绕过会话和平台权限，可能导致跨会话或跨用户发送。

### 可以只使用其中一部分吗？

可以。最安全的渐进方式是先只接入：

```text
office_list_templates
office_get_artifact_status
```

确认 identity、authorization、audit、schema 绑定测试完整后，再启用 create/render/send。

### 如何扩展新的 report type？

每新增一个 `report_type`，至少补齐：

- manifest enum
- MCP tool schema enum
- template/policy provisioning
- backend source query
- source hash 或 snapshot 签发
- renderer 支持
- response allow-list test
- forbidden fields test
- 真实平台 send smoke test

## License

当前 `pyproject.toml` 标记为 proprietary。若要公开复用，建议在项目根目录补充明确的 `LICENSE` 文件，并同步更新 `pyproject.toml`。
