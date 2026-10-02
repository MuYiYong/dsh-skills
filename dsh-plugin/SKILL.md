---
name: dsh-plugin
description: 创建、维护、排错和升级 DeepSeek Harness（DSH）独立 Cordis 插件与 bundle，支持本体智能应用、Host 工具及 Web UI 的接入、解耦与美化。用于 DSH 插件开发，不用于泛指 Codex 插件或只生成独立网页。
---

# DSH 插件开发与维护

交付独立于 DSH 源码的插件包，通过 profile/bundle 接入。默认用中文交流。用户说“本体智能”时，先按 ontology（实体、关系、规则、证据与动作）理解并注明假设；领域、数据源或目标不清楚时只询问影响实现的缺项，不擅自选择图数据库。

## 先识别任务与宿主

- 创建：明确用户操作、模型可调用能力、持久数据、UI 位置与验收流程。
- 维护/排错：保留已有实现和用户配置，从实际错误、最近改动、版本组合开始。
- 升级：读 [升级与验证](references/maintenance.md)，比较旧/新接口后再修改兼容声明。
- 仅评审：输出证据和建议，不安装插件或改 profile。

确定插件仓库、目标 profile、DSH 路径/版本。用户未指定源码时，可先检查 `/home/vesoft/deepseek-harness`；不要把它写死在生成的应用中。在 DSH 源码上只读取证，不把外部插件放进其 `packages/`，不改 agent-loop 或现有未提交文件。

```bash
python3 <skill目录>/scripts/probe_dsh.py --dsh /path/to/deepseek-harness --output ./dsh-baseline.json
```

报告包含版本、commit、脏文件路径和选定接口文件哈希，不读取凭据。它是差异线索，不是兼容性证明。读取目标版本的 `AGENTS.md`、`docs/architecture.zh.md`、`docs/development.zh.md`，随后只查所需服务/事件/slot。安装态优先使用可用的 `cordis_inspect_list/query`、包 README 与声明文件；Codex 环境没有这些工具时直接读源码，不虚构调用结果。知识路径见 [来源与基线](references/sources.md)。

## 创建路径

1. 读 [接入与边界](references/integration.md)。为所需能力列出服务 key、依赖、参数/结果、生命周期、存储所有者。领域代码不导入 DSH；Host 适配器通过 `ctx` 协作；UI 通过受支持的调用入口使用同一业务操作。仅在实际需要时拆多个包。
2. 有本体应用需求时读 [本体智能](references/ontology.md)。有界面时读 [UI 设计](references/ui.md)，先决定真实 slot 与主题，再写组件。
3. 小型外部插件可用无构建 JS 脚手架快速起步：

   ```bash
   python3 <skill目录>/scripts/scaffold.py --name @acme/ontology-workbench \
     --out /path/to/ontology-workbench --kind full --dsh-version 0.2.0-rc.2
   ```

   `host` 生成只读示例工具；`ui` 生成本地化的接入提示；`full` 合并两者。它们是可安装的接入起点，**不是完整本体应用**。使用实际宿主版本；生成器拒绝覆盖目录。说明文件列出独立验证和安装命令。复杂应用可以改为 TS，但 Host 与 Client 分别编译，浏览器最终仍输出 DSH lazy factory，不依赖 monorepo 的 tsdown 私有脚本。
4. 将示例替换为用户的真实流程；对 Config、模型输入、文件/网络与持久数据做边界校验。复用宿主工具审批、取消和工作区权限机制。读取当前目标版本的真实 API；不要把 `src/`、相对宿主路径或 `workspace:*` 留在发布产物里。
5. 验证业务、卸载/重挂与安装产物。UI 必须在真实 DSH slot 中检查；单独 HTML、截图或注册成功不能证明 UI 接入完成。按 [升级与验证](references/maintenance.md) 记录证据与未验证项。
6. 开发期使用隔离 `DSH_HOME`/profile。用户要求安装到正常 profile 时，通过宿主插件管理器或 `dsh plugin` 完成，保留返回的 `application`/warnings，不直接手改 profile 包清单。不得为解决安装失败自动授予版本豁免或允许依赖构建脚本。

## 不能省略的机制

- DSH 使用 `@deepseek-ai/cordis` 的 vendor 版本；上游 Cordis 说明原理，不替代目标 DSH API。不要打包第二套 Cordis 或 React。
- 必需服务在 `inject` 声明；可选能力用 `ctx.inject` 局部挂载。缺失必需服务时说明 pending 原因，不静默回退为成功。
- 注册、订阅、计时器、连接都有所属 context 与 disposer。跨 `agent.ctx` 注册还要归插件所有，二者任一卸载都能清理。持久业务数据不因插件卸载删除。
- waterfall 监听器若不拥有最终决策就返回 `next()`；修改决策保留其他字段。优先窄扩展点而不是重写提示词组装或循环。
- 模型可见上下文必须可从日志重建。外部插件不要直接 `Session.append()` 一个自定义 type；本体数据用插件存储，模型输出走现有工具结果/已支持注入接口。
- 版本兼容由 `peerDependencies` 中的 `@deepseek-ai/dsh`/`@deepseek-ai/dsh-*` 声明，`engines.dsh` 无效。只声称已验证的版本组合，不保证未来 DSH 改动永远零影响。

## 交付

给出插件路径、安装/启动命令、已验证宿主版本及测试结果。保留独立 manifest、打包文件、配置样例、兼容矩阵、迁移/回滚说明。区分已实现、已安装、已激活、已实测与待验证；用户请求的应用流程未完成时继续实现，不把脚手架当成成品。
