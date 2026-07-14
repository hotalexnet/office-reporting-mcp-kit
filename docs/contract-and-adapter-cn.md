# Office Reporting MCP Contract 与 Adapter 说明

## 1. Tool Contract

机器可校验 manifest 位于：

```text
contracts/office-reporting-mcp.manifest.json
```

项目实现必须把 manifest 与实际 tool schema 绑定测试。不要只改文档或只改代码。

## 2. 模型可见工具

### `office_list_templates`

列出当前 actor 被服务端授权的 Office 模板。可选过滤字段由项目定义，例如 `report_type/output_format/audience`。

禁止返回模板路径、文件路径、storage key、renderer command、raw data。

### `office_get_artifact_status`

查询当前 actor/session 可读 artifact 的状态。

不能凭 artifact id 读取他人 artifact 状态。不能返回 storage key、路径、media reference、source hash、actor context、recipient context。

### `office_create_report`

创建后端授权的 artifact intent。

允许字段必须是项目定义闭集或受控 scope/filter。业务事实必须由后端查询和签发。不能接收 raw data、template path、output path、renderer command、recipient 或 delivery 控制字段。

### `office_render_report`

渲染并校验已授权 artifact。

render 前必须重新授权当前 actor/session，并重新校验 source drift 或项目等价约束。渲染输出必须通过 artifact validator。

### `office_send_report`

为当前 actor/session 预留并解析 artifact delivery，由平台 adapter 完成实际发送。

模型不能传 recipient、delivery_request_id、mark_sent、media_tag。delivery 只能在平台发送成功后由 delivery adapter confirm。

## 3. Forbidden Model Fields

模型不得传递身份、授权、传输、渲染或 delivery 控制字段。

通用类别：

- identity/context：`context/profile_id/bot_id/wecom_user_id/conversation_id/session_id/chat_type/source_message_id`
- transport/client：`mcp_client_id/request_nonce/request_timestamp/runtime_instance_id`
- authorization conclusion：`role_name/actor_user_id/allowed_profiles/department/authorized`
- routing/domain：`domain`
- business/render control：`data/raw_data/template_path/output_path/storage_key/source_hash/snapshot_id/render_key/renderer_version/render_cli`
- delivery control：`recipient/media_tag/delivery_request_id/mark_sent`

项目实现必须用 schema `additionalProperties: false` 和 wrapper-side rejection 双层保护。

