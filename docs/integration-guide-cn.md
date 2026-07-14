# Office Reporting MCP Kit 接入指南

## 1. 复用边界

本仓库复用三层内容：

```text
Skill workflow layer
MCP contract layer
Project adapter layer
```

可复用的是 workflow、MCP tool contract、adapter protocol 和安全测试思路。不可复用的是任意项目的私有 gateway key、用户身份、profile、bot、数据库策略行、runtime patch、模板路径、存储路径或部署方式。

## 2. 核心不变量

1. 服务端 policy 是唯一授权边界。
2. identity/context 不进入模型可填写 schema。
3. domain 由项目 adapter 或服务端路由固定，不能让模型自由传。
4. 业务事实由后端查询和签发，不能使用模型 raw data。
5. 模板只能来自授权 template registry，不能使用模型传入路径。
6. response 必须使用 allow-list，不能透传内部 service view。
7. delivery 只能由 adapter 在平台发送成功后确认 `sent`。
8. media reference 不是权限凭证，不能从历史对话复用。

## 3. 标准工具链路

```text
office_list_templates
office_create_report
office_render_report
office_send_report
platform delivery confirm
```

`office_send_report` 只能返回待平台发送的受控 media reference。只有平台 adapter 成功发送后，后端才能把 delivery 标记为 `sent`。

## 4. Adapter 职责

| Adapter | 必须实现 | 禁止 |
|---|---|---|
| IdentityAdapter | 从 runtime 解析 caller/session/client audit context | 从模型参数读取 identity |
| AuthorizationAdapter | 后端重新解析 actor 并授权 domain/report/format/audience | 信任模型提供 role/authorized |
| TemplateRegistryAdapter | 返回授权模板 metadata 与不可变 hash | 返回模板路径 |
| ReportSourceAdapter | 查询后端事实并生成 source hash/snapshot | 使用模型 raw data |
| ArtifactStoreAdapter | 管理 intent/status/render/TTL/session 授权 | 仅凭 artifact id 跨用户读取 |
| RendererAdapter | 渲染并校验文件 | 暴露 renderer CLI 或输出路径 |
| DeliveryAdapter | reserve/resolve/send/confirm | 接收模型 recipient 或 mark_sent |
| AuditAdapter | 记录 client/runtime/session/tool/artifact/delivery | 把审计上下文透传给模型 |

## 5. 接入步骤

1. 复制 `skills/office-reporting/SKILL.md` 到目标 agent。
2. 从 `contracts/office-reporting-mcp.manifest.json` 创建项目 manifest。
3. 替换 `report_type/output_format/audience` enum 为项目服务端闭集。
4. 在工具 schema 中设置 `additionalProperties: false`。
5. 在 wrapper 中调用 `reject_model_controlled_fields()` 或等价 fail-closed 逻辑。
6. 实现 identity、authorization、template registry、source、artifact store、renderer、delivery、audit adapter。
7. 为 manifest 与实际 tool schema 添加绑定测试。
8. 为 forbidden fields 添加 pin test。
9. 跑 create -> render -> send -> platform confirm 的真实 smoke。

## 6. 接入前必须回答的问题

1. runtime 如何证明当前用户身份。
2. 后端如何重新解析 actor。
3. client registry 如何定义 active client、profile、domain、tool。
4. transport auth 用 trusted key、mTLS、HMAC 还是 OAuth2。
5. request nonce、timestamp、runtime instance 如何进入共享 replay guard。
6. domain 是固定路由还是多 domain adapter。
7. report type、format、audience 的授权矩阵在哪里。
8. template registry 是否使用不可变版本和 hash。
9. 业务事实如何由后端查询和签发。
10. artifact 生命周期、TTL、status 授权在哪里。
11. renderer 如何校验输出文件。
12. delivery adapter 如何判断平台发送成功。
13. 如何保证只有发送成功后 confirm sent。
14. audit 如何关联 client、runtime、session、tool、artifact、delivery。

如果任一项缺失，只能复用 Skill 文档和 MCP contract，不能启用 create/render/send。

