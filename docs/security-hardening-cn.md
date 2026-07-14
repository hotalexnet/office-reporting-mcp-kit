# Office Reporting 安全加固清单

## H1 模型边界

- 所有模型可见 schema 使用 `additionalProperties: false`。
- wrapper 层拒绝 forbidden model args。
- response 使用 allow-list，不透传内部对象。
- 缺 session/context 时 fail closed。
- 工具暴露由 capability gate 控制。

## H2 身份与传输

- `mcp_client_id` 由服务端注入，不能由模型设置。
- client registry 默认 fail closed。
- 外部 transport 必须有 registry、transport auth、client audit、anti-replay。
- runtime instance、transport auth mode、client id 写入 audit context。

## H3 复用边界

- Skill 不含项目私有凭证、路径、用户、profile、bot。
- MCP manifest 与实现测试绑定。
- 项目 adapter 明确，不把通用 contract 当成授权实现。

## H4 迁移与兼容

- legacy 工具必须明确兼容状态。
- 删除 legacy 前必须完成真实平台 smoke。
- rollback plan 必须保留。

## P4 业务扩展

每新增一个 `report_type` 都必须补齐：

- schema enum
- manifest enum
- template/policy provisioning
- backend source query
- source drift check
- renderer
- response allow-list test
-真实 platform smoke

