# 来源与兼容基线

核验日期：2026-10-02。当前实测目标：DSH `0.2.0-rc.2`，commit `639ed015397290b3745d163aafe02ffee4aa3f84`，Node `22.23.0`。源码工作区有既存 ui-settings-general 修改；未将它们当成公开 API，也未修改它们。本 skill 的描述是这份源码的快照；使用时重新探测目标版本。

## 来源优先级

运行实例的反射/实际行为 → 同版本源码与包声明 → 同版本开发文档 → 上游最新文档 → 通用原理。运行实例与文档冲突时记录冲突并做最小复现，不猜接口。

| 来源 | 用途 |
|---|---|
| [DSH 开发指南](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/development.zh.md) | 工具链、Host/Client 编译面、构建顺序 |
| [DSH 架构](https://github.com/deepseek-ai/deepseek-harness/blob/master/docs/architecture.zh.md) | profile、服务、事件与模型日志不变量 |
| [AGENTS.md](https://github.com/deepseek-ai/deepseek-harness/blob/master/AGENTS.md) | DSH 贡献规则；外部仓库无需照搬全仓 CI，但保留相关机制约束 |
| [Cordis](https://github.com/cordiverse/cordis) | 上游框架，README 明示 API 不稳定 |
| [论文](https://arxiv.org/abs/2608.25512) | A Programming Paradigm for Spatiotemporal Composability，2026-08-26，v1；此处采用摘要中的概念，未声称审阅全文证明 |
| `vendor/README.md` | DSH 的 scoped npm 名、固定上游来源及本地修改；不可用 npm cordis 随意替换 |

## 按需求查本地文件

以下均相对目标 DSH 根目录；安装包若无源码，则读已安装 packageDir 的 README、`lib/types` 与运行反射。

- 官方外部插件经验：`packages/preset/agent-preset/skills/cordis-plugin-development/SKILL.md` 及其 `references/{host-plugin,ui-plugin,practices,user-actions}.md`。这些机制已在本 skill 中自包含，目标环境无需安装该 skill。
- 包安装/版本检查：`apps/cli/README.zh.md`、`packages/boot/{app-boot,plugin-manager}/README.zh.md`。
- 工具：`docs/cookbook/adding-a-tool.zh.md`、`packages/core/tools/src/{index,schema}.ts`。
- UI：`packages/client/modules/README.zh.md`、`ui-slots/README.zh.md`、`ui-renderer/src/client/`、`locale/src/client/index.ts`、`docs/web-styling.zh.md`。
- 主题：`packages/client/ui-theme/src/styles/design-platform.css`；slot：`packages/client/ui-conversation/src/client/contract/slots.ts`，更换位置先查实际声明和渲染方。
- 调用 Host：`docs/api-gateway.zh.md`、`packages/interaction/commands/README.zh.md`（若路径移动用 rg 找包名）。不要认为外部插件声明一个 @Remote 装饰器就自动进入宿主生成图。
- Cordis 生命周期：`docs/cordis-primer.zh.md`、`docs/defensive-patterns.md`、`vendor/cordis/src/{fiber,registry,reflect}.ts`。

## 论文原理到工程要求

| 摘要概念 | 工程含义 | 证据 |
|---|---|---|
| Revertible effects / temporal composability | 所有运行时资源归 context，卸载可撤销注册与连接 | 卸载后工具/slot/监听器消失，无重复计时器 |
| Reactive coeffects / spatial composability | 服务依赖显式声明，由框架激活/停用 | 移除并恢复 provider，consumer 随之停用/恢复 |
| Context mediation | 组件经上下文协作，避免全局单例与私下修改其他插件 | 两实例与独立 scope 测试无交叉污染 |

可逆运行时副作用不代表已发送邮件、写入图数据库等业务行为可自动回滚。为业务写操作设计事务、幂等、审计和必要的补偿；热卸载只清理运行资源。
